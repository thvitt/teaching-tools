<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="3.1" expand-text="yes">

  <xsl:output method="text" />

  <xsl:param name="colorscheme">dark27</xsl:param>
  <xsl:param name="document">shape=point, color=1</xsl:param>
  <xsl:param name="element">shape=cds, color=2</xsl:param>
  <xsl:param name="attribute">shape=record, color=3</xsl:param>
  <xsl:param name="attribute-edge">style="dashed",dir="none"</xsl:param>
  <xsl:param name="text">shape=plaintext, fontcolor=4, labeljust=l</xsl:param>
  <xsl:param name="comment">shape=note, color=5, labeljust=l</xsl:param>
  <xsl:param name="pi">shape=diamond, color=6</xsl:param>

  <xsl:template match="/">digraph xml {{ rankdir=LR; node [colorscheme="{$colorscheme}"];
    {generate-id(.)} [shape=point;]; <xsl:apply-templates /> }} </xsl:template>

  <xsl:template match="element()"> {generate-id(.)} [label="{name()}", {$element}];
    {generate-id(..)} -&gt; {generate-id(.)}; <xsl:apply-templates select="@*, node()" />
  </xsl:template>

  <xsl:template match="text()">
    <xsl:if test="normalize-space() != ''">
      <xsl:variable name="content"
        select="replace(replace(normalize-space(.), '\\', '\\\\'), '&quot;', '\\&quot;')" />
      {generate-id(.)} [label="{$content}", {$text}]; {generate-id(..)} -&gt; {generate-id(.)}; </xsl:if>
  </xsl:template>

  <xsl:template match="@*">
    {generate-id(.)} [label="{name()}|{.}", {$attribute}];
    {generate-id(..)} -&gt; {generate-id(.)} [{$attribute-edge}];
  </xsl:template>

  <xsl:template match="comment()">
    {generate-id(.)} [label="{normalize-space(.)}", {$comment}];
    {generate-id(..)} -&gt; {generate-id(.)};
  </xsl:template>

  <xsl:template match="processing-instruction()">
    {generate-id(.)} [label="{name()}",{$pi}];
    {generate-id(..)} -&gt; {generate-id(.)};
  </xsl:template>

</xsl:stylesheet>
