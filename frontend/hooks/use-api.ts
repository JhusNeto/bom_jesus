import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/services/api"

/**
 * Custom hook for API queries
 * Example usage:
 * const { data, isLoading, error } = useApiQuery(['users'], '/users')
 */
export function useApiQuery<T = any>(
  queryKey: string[],
  endpoint: string,
  options?: {
    enabled?: boolean
    staleTime?: number
  }
) {
  return useQuery<T>({
    queryKey,
    queryFn: async () => {
      const response = await api.get<T>(endpoint)
      return response.data
    },
    enabled: options?.enabled ?? true,
    staleTime: options?.staleTime ?? 60000,
  })
}

/**
 * Custom hook for API mutations
 * Example usage:
 * const mutation = useApiMutation(['users'], 'POST', '/users')
 * mutation.mutate({ name: 'John' })
 */
export function useApiMutation<TData = any, TVariables = any>(
  queryKey: string[],
  method: "POST" | "PUT" | "PATCH" | "DELETE" = "POST",
  endpoint: string
) {
  const queryClient = useQueryClient()

  return useMutation<TData, Error, TVariables>({
    mutationFn: async (data: TVariables) => {
      const response = await api[method.toLowerCase() as "post" | "put" | "patch" | "delete"]<TData>(
        endpoint,
        data
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey })
    },
  })
}

