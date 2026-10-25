const BASE = import.meta.env.VITE_API_URL || '/api';
export async function api(path, method = 'GET', body) {
  let response;
  try {
    response = await fetch(`${BASE}${path}`, {method, headers: body ? {'Content-Type':'application/json'} : {}, body: body ? JSON.stringify(body) : undefined});
  } catch {
    throw new Error('Сервер недоступен. Проверьте, что backend запущен на порту 8000.');
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(typeof data.detail === 'string' ? data.detail : Array.isArray(data.detail) ? data.detail.map(e => `${e.loc.slice(1).join('.')}: ${e.msg}`).join('; ') : `Ошибка ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}
