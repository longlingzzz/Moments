const BASE_URL = 'http://127.0.0.1:8000/api';

function request({ url, method = 'GET', data = {}, header = {} }) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      success: (res) => {
        // 2xx 视为成功
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject({ status: res.statusCode, data: res.data });
        }
      },
      fail: (err) => reject(err)
    });
  });
}

function authHeader() {
  const token = getToken();
  return token ? { Authorization: `Token ${token}` } : {};
}

export async function loginApi({ username, password }) {
  return request({
    url: '/auth/login/',
    method: 'POST',
    data: { username, password }
  });
}

export async function registerApi({ username, password, email, first_name, last_name }) {
  return request({
    url: '/users/',
    method: 'POST',
    data: { username, password, email, first_name, last_name }
  });
}

export async function fetchMe() {
  return request({
    url: '/users/me/',
    method: 'GET',
    header: { ...authHeader() }
  });
}

export async function updateMe(payload) {
  return request({
    url: '/users/me/',
    method: 'PATCH',
    data: payload,
    header: { ...authHeader() }
  });
}

export async function changePassword({ old_password, new_password }) {
  return request({
    url: '/users/me/password/',
    method: 'POST',
    data: { old_password, new_password },
    header: { ...authHeader() }
  });
}

export function saveToken(token) {
  uni.setStorageSync('auth_token', token);
}

export function clearToken() {
  uni.removeStorageSync('auth_token');
  uni.removeStorageSync('current_user');
}

export function getToken() {
  return uni.getStorageSync('auth_token');
}
