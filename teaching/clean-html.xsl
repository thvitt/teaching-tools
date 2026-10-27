<xsl:stylesheet version="3.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xpath-default-namespace="http://www.w3.org/1999/html">
  <xsl:output method="html" version="5" />
  <xsl:mode on-no-match="shallow-copy" />

  <xsl:template match="@style"></xsl:template>
  <xsl:template match="span[not(@id|@xml:id|@xml:lang)]"><xsl:apply-templates></xsl:apply-templates></xsl:template>
  <xsl:template
    match="(h1|h2|h3|h4|h5|h6)/(strong|b)[not(@following-sibling::node() | preceding-sibling::node())]"></xsl:template>

</xsl:stylesheet>
