import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import OutlawStatusIndicator from '../../src/components/character/display/OutlawStatusIndicator';

// Mock the API call
jest.mock('../../src/api/character', () => ({
  fetchOutlawStatus: jest.fn().mockImplementation((characterId) => 
    Promise.resolve({
      isOutlaw: true,
      severity: 'major',
      activeConsequences: [
        { type: 'bounty', severity: 'major', expiresAt: null },
        { type: 'npc_hostility', severity: 'major', expiresAt: '2024-07-01T12:00:00Z' },
      ],
    })
  ),
}));

describe('OutlawStatusIndicator', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state initially', () => {
    render(<OutlawStatusIndicator characterId={1} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays outlaw status chip when data is loaded', async () => {
    render(<OutlawStatusIndicator characterId={1} />);
    
    await waitFor(() => {
      expect(screen.getByText('OUTLAW (MAJOR)')).toBeInTheDocument();
    });
  });

  it('shows tooltip with active consequences', async () => {
    render(<OutlawStatusIndicator characterId={1} />);
    
    await waitFor(() => {
      const chip = screen.getByText('OUTLAW (MAJOR)');
      // Trigger tooltip
      chip.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
      
      expect(screen.getByText('Active Consequences:')).toBeInTheDocument();
      expect(screen.getByText(/bounty \(Severity: major\)/)).toBeInTheDocument();
      expect(screen.getByText(/npc hostility \(Severity: major\)/)).toBeInTheDocument();
    });
  });

  it('uses correct color based on severity', async () => {
    render(<OutlawStatusIndicator characterId={1} />);
    
    await waitFor(() => {
      const chip = screen.getByText('OUTLAW (MAJOR)');
      expect(chip).toHaveStyle({ backgroundColor: expect.stringMatching(/error/) });
    });
  });

  it('returns null when not an outlaw', async () => {
    // Override mock for this test
    require('../../src/api/character').fetchOutlawStatus.mockImplementationOnce(() =>
      Promise.resolve({ isOutlaw: false })
    );

    const { container } = render(<OutlawStatusIndicator characterId={1} />);
    
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });
}); 