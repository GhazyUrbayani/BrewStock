// Dibantu AI: KpiCardTest
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import KpiCard from './KpiCard'

describe('KpiCard', () => {
  it('shows positive trend and good status', () => {
    const { container } = render(
      <KpiCard
        label="Revenue"
        value="120 cup"
        trend="↑ 12% vs minggu lalu"
        trendDirection="up"
        targetText="Target: > 100"
        statusBadge="✅"
        statusCondition="good"
      />,
    )

    expect(screen.getByText('Revenue')).toBeTruthy()
    expect(screen.getByText('120 cup')).toBeTruthy()
    expect(screen.getByText('↑ 12% vs minggu lalu')).toBeTruthy()
    expect(screen.getByText('Target: > 100')).toBeTruthy()
    expect(screen.getByText('✅')).toBeTruthy()

    const deltaRow = container.querySelector('.kpi-card-delta')
    const statusBadge = container.querySelector('.kpi-card-status')

    expect(deltaRow?.className).toContain('up')
    expect(statusBadge?.className).toContain('good')
  })

  it('shows negative trend and critical status', () => {
    const { container } = render(
      <KpiCard
        label="Orders"
        value="80 cup"
        trend="↓ 9% vs minggu lalu"
        trendDirection="down"
        targetText="Target: > 100"
        statusBadge="Kritis"
        statusCondition="critical"
      />,
    )

    expect(screen.getByText('Orders')).toBeTruthy()
    expect(screen.getByText('80 cup')).toBeTruthy()
    expect(screen.getByText('↓ 9% vs minggu lalu')).toBeTruthy()
    expect(screen.getByText('Target: > 100')).toBeTruthy()
    expect(screen.getByText('Kritis')).toBeTruthy()

    const deltaRow = container.querySelector('.kpi-card-delta')
    const statusBadge = container.querySelector('.kpi-card-status')

    expect(deltaRow?.className).toContain('down')
    expect(statusBadge?.className).toContain('critical')
  })
})
