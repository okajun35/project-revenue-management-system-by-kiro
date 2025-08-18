async function fetchMappingSuggestions(columns) {
  try {
    const res = await fetch('/import/suggest-mapping', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ columns })
    });
    if (!res.ok) return {};
    const data = await res.json();
    return data.mapping || {};
  } catch (e) {
    console.warn('suggest-mapping failed', e);
    return {};
  }
}

window.applyMappingSuggestions = async function(columns) {
  const suggestions = await fetchMappingSuggestions(columns);
  for (const [field, col] of Object.entries(suggestions)) {
    if (!col) continue;
    const select = document.querySelector(`select[name="mapping_${field}"]`);
    if (select && !select.value) {
      select.value = col;
      select.dispatchEvent(new Event('change'));
    }
  }
}
