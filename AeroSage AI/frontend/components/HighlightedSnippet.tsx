export default function HighlightedSnippet({
  snippet,
  span,
}: {
  snippet: string;
  span: string;
}) {
  const trimmedSpan = span.trim();
  const index = trimmedSpan ? snippet.indexOf(trimmedSpan) : -1;

  if (index === -1) {
    return <p className="text-sm text-foreground/90">{snippet}</p>;
  }

  const before = snippet.slice(0, index);
  const match = snippet.slice(index, index + trimmedSpan.length);
  const after = snippet.slice(index + trimmedSpan.length);

  return (
    <p className="text-sm text-foreground/90">
      {before}
      <mark className="evidence-highlight">{match}</mark>
      {after}
    </p>
  );
}
