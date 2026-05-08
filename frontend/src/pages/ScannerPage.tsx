// Dibantu AI: ScannerPage
import { type ChangeEvent, type DragEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import './ScannerPage.css'
import type { ScannerResponse, StockUpdateResponse } from '../types'

type ScannerPageProps = {
  authRequest: <T>(
    pathValue: string,
    optionsValue?: { method?: string; body?: unknown },
  ) => Promise<T>
}

type ScannerStatus = {
  tone: 'neutral' | 'success' | 'danger'
  message: string
}

const numberFormatter = new Intl.NumberFormat('id-ID', {
  maximumFractionDigits: 1,
})

function formatNumber(value: number) {
  return numberFormatter.format(value)
}

function readErrorMessage(errorValue: unknown) {
  if (errorValue instanceof Error) {
    return errorValue.message
  }
  return 'Proses scanner gagal'
}

const paletteItems = ['#0f766e', '#f97316', '#0ea5e9', '#db2777', '#7c3aed']

export default function ScannerPage({ authRequest }: ScannerPageProps) {
  const [scannerResult, setScannerResult] = useState<ScannerResponse | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [status, setStatus] = useState<ScannerStatus | null>(null)
  const [imageLoaded, setImageLoaded] = useState(false)
  const imageRef = useRef<HTMLImageElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  const imageSource = scannerResult?.annotatedImageBase64 || previewUrl

  const classColorMap = useMemo(() => {
    const mapValue = new Map<string, string>()
    scannerResult?.detections.forEach((itemValue, indexValue) => {
      mapValue.set(itemValue.className, paletteItems[indexValue % paletteItems.length])
    })
    return mapValue
  }, [scannerResult])

  const scanFile = useCallback(
    async (fileValue: File) => {
      setIsScanning(true)
      setStatus(null)
      setScannerResult(null)
      try {
        const formData = new FormData()
        formData.append('image', fileValue)

        const responseValue = await authRequest<ScannerResponse>('/api/v1/scanner/detect', {
          method: 'POST',
          body: formData,
        })
        setScannerResult(responseValue)
        setStatus({ tone: 'success', message: 'Scan selesai' })
      } catch (errorValue) {
        setStatus({ tone: 'danger', message: readErrorMessage(errorValue) })
      } finally {
        setIsScanning(false)
      }
    },
    [authRequest],
  )

  const handleFile = useCallback(
    (fileValue: File) => {
      setSelectedFile(fileValue)
      const nextUrl = URL.createObjectURL(fileValue)
      setPreviewUrl(nextUrl)
      void scanFile(fileValue)
    },
    [scanFile],
  )

  const handleFileInput = useCallback(
    (eventValue: ChangeEvent<HTMLInputElement>) => {
      const fileValue = eventValue.target.files?.[0]
      if (fileValue) {
        handleFile(fileValue)
      }
    },
    [handleFile],
  )

  const handleDrop = useCallback(
    (eventValue: DragEvent<HTMLButtonElement>) => {
      eventValue.preventDefault()
      setIsDragging(false)
      const fileValue = eventValue.dataTransfer.files?.[0]
      if (fileValue) {
        handleFile(fileValue)
      }
    },
    [handleFile],
  )

  const suggestedItems = scannerResult?.suggestedStockUpdate ?? []

  const handleUpdateStock = useCallback(async () => {
    if (suggestedItems.length === 0) {
      setStatus({ tone: 'neutral', message: 'Tidak ada stok untuk diupdate' })
      return
    }

    setIsUpdating(true)
    setStatus(null)
    try {
      for (const itemValue of suggestedItems) {
        await authRequest<StockUpdateResponse>(
          `/api/v1/inventory/${itemValue.skuId}/stock`,
          {
            method: 'PATCH',
            body: { currentStock: itemValue.detectedCount },
          },
        )
      }
      setStatus({ tone: 'success', message: 'Stok berhasil diperbarui' })
    } catch (errorValue) {
      setStatus({ tone: 'danger', message: readErrorMessage(errorValue) })
    } finally {
      setIsUpdating(false)
    }
  }, [authRequest, suggestedItems])

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  useEffect(() => {
    setImageLoaded(false)
  }, [imageSource])

  useEffect(() => {
    const canvasValue = canvasRef.current
    const imageValue = imageRef.current
    if (!canvasValue || !imageValue) {
      return
    }

    const contextValue = canvasValue.getContext('2d')
    if (!contextValue) {
      return
    }

    const rectValue = imageValue.getBoundingClientRect()
    canvasValue.width = rectValue.width
    canvasValue.height = rectValue.height
    contextValue.clearRect(0, 0, canvasValue.width, canvasValue.height)

    if (!scannerResult || !imageLoaded) {
      return
    }
    const naturalWidth = imageValue.naturalWidth || rectValue.width
    const naturalHeight = imageValue.naturalHeight || rectValue.height
    if (naturalWidth === 0 || naturalHeight === 0) {
      return
    }

    const scaleX = rectValue.width / naturalWidth
    const scaleY = rectValue.height / naturalHeight

    scannerResult.detections.forEach((itemValue) => {
      const colorValue = classColorMap.get(itemValue.className) ?? '#0f766e'
      contextValue.strokeStyle = colorValue
      contextValue.lineWidth = 2
      contextValue.fillStyle = colorValue
      contextValue.font = '12px "DM Sans", sans-serif'

      itemValue.boundingBoxes.forEach((boxValue) => {
        const xValue = boxValue.x1 * scaleX
        const yValue = boxValue.y1 * scaleY
        const widthValue = (boxValue.x2 - boxValue.x1) * scaleX
        const heightValue = (boxValue.y2 - boxValue.y1) * scaleY

        contextValue.strokeRect(xValue, yValue, widthValue, heightValue)
        contextValue.fillRect(xValue, Math.max(0, yValue - 16), 72, 16)
        contextValue.fillStyle = '#ffffff'
        contextValue.fillText(itemValue.className, xValue + 4, Math.max(12, yValue - 4))
        contextValue.fillStyle = colorValue
      })
    })
  }, [classColorMap, imageLoaded, scannerResult, imageSource])

  const detectionCards = scannerResult?.detections ?? []

  return (
    <section className="scanner-page" aria-label="Scanner stok">
      <header className="scanner-header">
        <div>
          <p className="scanner-eyebrow">Scanner</p>
          <h2 className="scanner-title">Deteksi stok via foto</h2>
        </div>
        <div className="scanner-meta">
          <span className="scanner-pill">YOLOv8</span>
          {scannerResult ? (
            <span className="scanner-pill">{scannerResult.inferenceTimeMs} ms</span>
          ) : null}
        </div>
      </header>

      <div className="scanner-grid">
        <div className="scanner-card">
          <button
            type="button"
            className={`scanner-upload ${isDragging ? 'dragging' : ''}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={(eventValue) => {
              eventValue.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            aria-label="Upload foto stok"
          >
            <input
              id="scanner-input"
              type="file"
              accept="image/*"
              onChange={handleFileInput}
              aria-label="Pilih foto stok"
              className="scanner-input"
              ref={inputRef}
            />
            <div>
              <strong>Drag & drop foto</strong>
              <p>Klik untuk memilih gambar rak</p>
            </div>
          </button>

          <div className="scanner-preview" aria-label="Hasil scan">
            {isScanning ? (
              <div className="scanner-skeleton" aria-label="Memuat hasil scan" />
            ) : imageSource ? (
              <div className="scanner-image-frame">
                <img
                  ref={imageRef}
                  src={imageSource}
                  alt="Preview scanner"
                  className="scanner-image"
                  onLoad={() => {
                    setImageLoaded(true)
                  }}
                />
                <canvas ref={canvasRef} className="scanner-canvas" />
              </div>
            ) : (
              <div className="scanner-placeholder">Belum ada gambar.</div>
            )}
          </div>

          <div className="scanner-status" role="status">
            {status ? (
              <span className={`scanner-status-${status.tone}`}>{status.message}</span>
            ) : (
              <span className="scanner-status-neutral">
                {selectedFile ? selectedFile.name : 'Pilih foto untuk mulai scan.'}
              </span>
            )}
          </div>
        </div>

        <div className="scanner-card">
          <div className="scanner-section">
            <h3>Ringkasan deteksi</h3>
            <div className="scanner-list">
              {detectionCards.length === 0 ? (
                <div className="scanner-placeholder">Belum ada deteksi.</div>
              ) : (
                detectionCards.map((itemValue) => (
                  <div key={itemValue.className} className="scanner-item">
                    <div>
                      <strong>{itemValue.className}</strong>
                      <p>{formatNumber(itemValue.count)} item</p>
                    </div>
                    <span className="scanner-confidence">
                      {Math.round(itemValue.confidence * 100)}%
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="scanner-section">
            <h3>Update stok</h3>
            <div className="scanner-update-list">
              {suggestedItems.length === 0 ? (
                <div className="scanner-placeholder">Tidak ada rekomendasi stok.</div>
              ) : (
                suggestedItems.map((itemValue) => (
                  <div key={itemValue.skuId} className="scanner-update-row">
                    <span>{itemValue.skuId}</span>
                    <span>{formatNumber(itemValue.detectedCount)}</span>
                  </div>
                ))
              )}
            </div>
            <button
              type="button"
              className="primary-button"
              onClick={() => void handleUpdateStock()}
              disabled={isUpdating || suggestedItems.length === 0}
              aria-label="Konfirmasi update stok"
            >
              {isUpdating ? 'Memperbarui...' : 'Konfirmasi update stok'}
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

export type { ScannerPageProps }
