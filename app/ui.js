const form = document.querySelector('#convert');
const status = document.querySelector('#status');
const output = document.querySelector('#result');
const download = document.querySelector('#download');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  document.querySelector('#submit').disabled = true;
  download.disabled = true;
  output.value = '';
  status.textContent = 'Fetching and converting article…';
  try {
    const response = await fetch(`/api/articles/${encodeURIComponent(form.article.value)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Invalid article ID');
    output.value = data.markdown;
    download.disabled = false;
    status.textContent = `Converted: ${data.title}`;
  } catch (error) { status.textContent = error.message; }
  finally { document.querySelector('#submit').disabled = false; }
});
download.addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([output.value], {type: 'text/markdown;charset=utf-8'}));
  const a = document.createElement('a');
  a.href = url; a.download = 'article.md'; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
