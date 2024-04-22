export class BaseApi {
    base_url: string;
    constructor() {
        this.base_url = import.meta.env.VITE_API_URL;
    }
    public async Get<T>(url: string, params: URLSearchParams = new URLSearchParams({})): Promise<T[] | T> {
        const response = await fetch(`${this.base_url}${url}?` + params, {
            headers: {
                'Authorization': get_bearer_token()
            }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch');
        }
        const data = await response.json();
        return data;
    }
    public async GetOne<T>(url: string, params: URLSearchParams = new URLSearchParams({})): Promise<T> {
        const response = await fetch(`${this.base_url}${url}?` + params, {
            headers: {
                'Authorization': get_bearer_token()
            }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch');
        }
        const data = await response.json();
        return data;
    }
    public async GetById<T>(url: string, id: string): Promise<T> {
        const response = await fetch(`${this.base_url}${url}/${id}`, {
            headers: {
                'Authorization': get_bearer_token()
            }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch');
        }
        const data = await response.json();
        return data;
    }
    public async create<T>(url: string, data: T | any): Promise<T> {
        const response = await fetch(`${this.base_url}/${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': get_bearer_token()
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json()
            if (err) {
                throw new Error(err.message)
            }
            throw new Error('Failed to create');
        }
        const responseData = await response.json();
        return responseData;
    }
    public async update<T>(url: string, data: T | any): Promise<T> {
        const response = await fetch(`${this.base_url}${url}/${data.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': get_bearer_token()
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error('Failed to update');
        }
        const responseData = await response.json();
        return responseData;
    }
    public async delete<T>(url: string, id: string): Promise<T> {
        const response = await fetch(`${this.base_url}${url}/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': get_bearer_token()
            }
        });
        if (!response.ok) {
            throw new Error('Failed to delete');
        }
        const responseData = await response.json();
        return responseData;
    }
}
const get_bearer_token = () => {
    let token = localStorage.getItem('access_token');
    if (token) {
        return `Bearer ${token}`;
    }
    return '';
}