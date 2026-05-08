const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? ''

type ApiRequestOptions = {
  method?: string
  body?: unknown
  accessToken?: string
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function buildUrl(pathValue: string) {
  const normalizedPath = pathValue.startsWith('/') ? pathValue : `/${pathValue}`
  if (apiBaseUrl === '') {
    return normalizedPath
  }
  return `${apiBaseUrl}${normalizedPath}`
}

function readErrorMessage(payloadValue: unknown) {
  if (
    typeof payloadValue === 'object' &&
    payloadValue !== null &&
    'detail' in payloadValue
  ) {
    const detailValue = payloadValue.detail
    if (typeof detailValue === 'string') {
      return detailValue
    }
    if (Array.isArray(detailValue)) {
      return detailValue
        .map((itemValue) => {
          if (typeof itemValue === 'object' && itemValue !== null && 'msg' in itemValue) {
            return String(itemValue.msg)
          }
          return String(itemValue)
        })
        .join(', ')
    }
  }
  return 'Request gagal diproses'
}

function parsePayload(textValue: string) {
  if (textValue === '') {
    return null
  }

  try {
    return JSON.parse(textValue) as unknown
  } catch {
    throw new Error('Response backend tidak valid')
  }
}

export async function apiRequest<TResponse>(
  pathValue: string,
  optionsValue: ApiRequestOptions = {},
) {
  const headersValue = new Headers()
  headersValue.set('Accept', 'application/json')

  const isFormData = optionsValue.body instanceof FormData

  if (optionsValue.body !== undefined && !isFormData) {
    headersValue.set('Content-Type', 'application/json')
  }

  if (optionsValue.accessToken) {
    headersValue.set('Authorization', `Bearer ${optionsValue.accessToken}`)
  }

  const responseValue = await fetch(buildUrl(pathValue), {
    method: optionsValue.method ?? 'GET',
    headers: headersValue,
    body:
      optionsValue.body === undefined
        ? undefined
        : isFormData
          ? optionsValue.body
          : JSON.stringify(optionsValue.body),
  })

  const textValue = await responseValue.text()
  const payloadValue = parsePayload(textValue)

  if (!responseValue.ok) {
    throw new ApiError(readErrorMessage(payloadValue), responseValue.status)
  }

  return payloadValue as TResponse
}
