<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema" version="3.1" expand-text="yes"
  xmlns:t="https://thorstenvitt.net/fn">

  <xsl:output method="text" />

  <xsl:param name="colorscheme">dark27</xsl:param>
  <xsl:param name="document">shape=point, color=1</xsl:param>
  <xsl:param name="element">shape=cds, color=2</xsl:param>
  <xsl:param name="attribute">shape=record, color=3</xsl:param>
  <xsl:param name="attribute-edge">style="dashed",dir="none"</xsl:param>
  <xsl:param name="text">shape=plaintext, fontcolor=4, labeljust=l</xsl:param>
  <xsl:param name="whitespace"></xsl:param>
  <xsl:param name="comment">shape=note, color=5, labeljust=l</xsl:param>
  <xsl:param name="pi">shape=diamond, color=6</xsl:param>
  <xsl:param name="shorten-min" as="xs:integer">20</xsl:param>
  <xsl:param name="shorten-max" as="xs:integer">20</xsl:param>

  <xsl:function name="t:shorten" as="xs:string">
    <xsl:param name="text" as="xs:string" />
    <xsl:param name="min-length" as="xs:integer" />
    <xsl:param name="max-length" as="xs:integer" />
    <xsl:param name="where" />
    <xsl:choose>
      <xsl:when test="string-length($text) > $min-length">
        <xsl:choose>
          <xsl:when test="$where = ('center', 'middle')">
            <xsl:value-of
              select="substring($text, 1, floor($max-length div 2)) || '…' || substring($text, ceiling(string-length($text) - $max-length div 2))"
            />
          </xsl:when>
          <xsl:when test="$where = ('start', 'beginning', 'left')">
            <xsl:value-of select="'…' || substring($text, string-length($text) - $max-length - 1)" />
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="substring($text, 1, $max-length - 1) || '…'" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <xsl:template match="/">digraph xml {{ rankdir=LR; node [colorscheme="{$colorscheme}"];
    {generate-id(.)} [shape=point;]; <xsl:apply-templates /> }} </xsl:template>

  <xsl:template match="element()"> {generate-id(.)} [label="{name()}", {$element}];
    {generate-id(..)} -&gt; {generate-id(.)}; <xsl:apply-templates select="@*, node()" />
  </xsl:template>

  <xsl:template match="text()">
    <xsl:choose>
      <xsl:when test="normalize-space() != ''">
        <xsl:variable name="content_"
          select="replace(replace(normalize-space(.), '\\', '\\\\'), '&quot;', '\\&quot;')" />
        <xsl:variable
          name="content" select="t:shorten($content_, $shorten-min, $shorten-max, 'end')" />
        {generate-id(.)} [label="{$content}", {$text}]; {generate-id(..)} -&gt; {generate-id(.)}; </xsl:when>
      <xsl:when test="$whitespace != ''">
        {generate-id(.)} [label="{$whitespace}", {$text}]; {generate-id(..)} -&gt; {generate-id(.)}; </xsl:when>
      <xsl:otherwise />
    </xsl:choose>
  </xsl:template>

  <xsl:template match="@*"> {generate-id(.)} [label="{name()}|{t:shorten(., 20, 20, 'middle')}",
    {$attribute}]; {generate-id(..)}
    -&gt; {generate-id(.)} [{$attribute-edge}]; </xsl:template>

  <xsl:template match="comment()"> {generate-id(.)} [label="{normalize-space(.)}", {$comment}];
    {generate-id(..)} -&gt; {generate-id(.)}; </xsl:template>

  <xsl:template match="processing-instruction()"> {generate-id(.)} [label="{name()}",{$pi}];
    {generate-id(..)} -&gt; {generate-id(.)}; </xsl:template>

</xsl:stylesheet>
