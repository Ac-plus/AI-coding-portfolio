function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderInline(text) {
  let output = escapeHtml(text);

  output = output.replace(/`([^`]+)`/g, "<code>$1</code>");
  output = output.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  output = output.replace(/\*([^*]+)\*/g, "<em>$1</em>");
  output = output.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noreferrer">$1</a>',
  );

  return output;
}

function renderBlock(block) {
  const trimmed = block.trim();
  if (!trimmed) {
    return "";
  }

  const codeMatch = trimmed.match(/^```([^\n]*)\n([\s\S]*?)\n```$/);
  if (codeMatch) {
    const language = codeMatch[1].trim();
    const code = escapeHtml(codeMatch[2]);
    const languageBadge = language ? `<span class="code-language">${language}</span>` : "";
    return `<pre class="markdown-code">${languageBadge}<code>${code}</code></pre>`;
  }

  const lines = trimmed.split("\n");

  if (lines.every((line) => /^[-*]\s+/.test(line))) {
    const items = lines.map((line) => `<li>${renderInline(line.replace(/^[-*]\s+/, ""))}</li>`).join("");
    return `<ul>${items}</ul>`;
  }

  if (lines.every((line) => /^\d+\.\s+/.test(line))) {
    const items = lines.map((line) => `<li>${renderInline(line.replace(/^\d+\.\s+/, ""))}</li>`).join("");
    return `<ol>${items}</ol>`;
  }

  if (lines.every((line) => /^>\s?/.test(line))) {
    const content = lines.map((line) => renderInline(line.replace(/^>\s?/, ""))).join("<br />");
    return `<blockquote>${content}</blockquote>`;
  }

  const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
  if (headingMatch) {
    const level = headingMatch[1].length;
    return `<h${level}>${renderInline(headingMatch[2])}</h${level}>`;
  }

  return `<p>${lines.map((line) => renderInline(line)).join("<br />")}</p>`;
}

export function markdownToHtml(markdown = "") {
  return markdown
    .replace(/\r\n/g, "\n")
    .split(/\n{2,}/)
    .map((block) => renderBlock(block))
    .join("");
}
