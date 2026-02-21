import { apiRequest } from './client';

export interface Product {
  id: string;
  name: string;
}

export interface Location {
  id: string;
  name: string;
  type: string;
}

export interface Client {
  id: string;
  name: string;
}

export interface Store {
  id: string;
  clientId: string;
  name: string;
}

export interface Reason {
  id: string;
  type: 'LOSS' | 'RETURN';
  name: string;
}

export function listProducts() {
  return apiRequest<Product[]>('/catalog/products');
}

export function listLocations() {
  return apiRequest<Location[]>('/catalog/locations');
}

export function listClients() {
  return apiRequest<Client[]>('/catalog/clients');
}

export function listStores(clientId?: string) {
  const query = clientId ? `?clientId=${encodeURIComponent(clientId)}` : '';
  return apiRequest<Store[]>(`/catalog/stores${query}`);
}

export function listReasons(type: 'LOSS' | 'RETURN') {
  return apiRequest<Reason[]>(`/catalog/reasons?type=${type}`);
}
