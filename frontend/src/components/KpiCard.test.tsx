// Dibantu AI: KpiCardTest
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import KpiCard from './KpiCard'

describe('KpiCard', () => {
  it('shows positive delta and on-target status', () => {
    const { container } = render(
      <KpiCard
        label="Revenue"
        value={120}
        unit="cup"
        delta={14}
        deltaPercent={12}
        target={100}
        targetLabel="Target"
      />,
    )

    expect(screen.getByText('Revenue')).toBeTruthy()
    expect(screen.getByText('120')).toBeTruthy()
    expect(screen.getByText('cup')).toBeTruthy()
    expect(screen.getByText('+14')).toBeTruthy()
    expect(screen.getByText('12%')).toBeTruthy()
    expect(screen.getByText('Di atas target')).toBeTruthy()

    const deltaRow = container.querySelector('.kpi-card-delta')
    const statusBadge = container.querySelector('.kpi-card-status')

    expect(deltaRow?.className).toContain('positive')
    expect(statusBadge?.className).toContain('positive')
  })

  it('shows negative delta and below-target status', () => {
    const { container } = render(
      <KpiCard
        label="Orders"
        value={80}
        unit="cup"
        delta={-8}
        deltaPercent={-9}
        target={100}
        targetLabel="Target"
      />,
    )

    expect(screen.getByText('Orders')).toBeTruthy()
    expect(screen.getByText('-8')).toBeTruthy()
    expect(screen.getByText('9%')).toBeTruthy()
    expect(screen.getByText('Di bawah target')).toBeTruthy()

    const deltaRow = container.querySelector('.kpi-card-delta')
    const statusBadge = container.querySelector('.kpi-card-status')

    expect(deltaRow?.className).toContain('negative')
    expect(statusBadge?.className).toContain('negative')
  })
})
