// Connect the article form to the API and offer the returned Markdown as a file.
const form = document.querySelector('#convert');
const status = document.querySelector('#status');
const output = document.querySelector('#result');
const download = document.querySelector('#download');
form.addEventListener('submit', async (event) => {
  // Stay on this page and prevent repeat submissions while conversion is pending.
  event.preventDefault();
  document.querySelector('#submit').disabled = true;
  download.disabled = true;
  output.value = '';
  status.textContent = 'Fetching and converting article…';
  try {
    const response = await fetch(`/api/articles/${encodeURIComponent(form.article.value)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Invalid article ID');
    // Display untrusted article content as plain text, not rendered HTML.
    output.value = data.markdown;
    download.disabled = false;
    status.textContent = `Converted: ${data.title}`;
  } catch (error) { status.textContent = error.message; }
  finally { document.querySelector('#submit').disabled = false; }
});
download.addEventListener('click', () => {
  // Build the download in the browser; no additional server request is needed.
  const url = URL.createObjectURL(new Blob([output.value], {type: 'text/markdown;charset=utf-8'}));
  const a = document.createElement('a');
  a.href = url; a.download = 'article.md'; a.click();
  // Release the temporary URL after allowing the download to start.
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
