import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AppealSystem from '../../src/components/appeal/AppealSystem';
import AppealForm from '../../src/components/appeal/AppealForm';
import AppealStatus from '../../src/components/appeal/AppealStatus';
import { AppealProvider } from '../../src/contexts/AppealContext';

// Mock the API calls
jest.mock('../../src/api/appeals', () => ({
  submitAppeal: jest.fn().mockImplementation((data) => 
    Promise.resolve({ id: 'test-appeal-id', ...data })
  ),
  getAppealStatus: jest.fn().mockImplementation((appealId) =>
    Promise.resolve({
      id: appealId,
      status: 'pending',
      submittedAt: new Date().toISOString(),
      response: null
    })
  ),
  getActiveAppeals: jest.fn().mockImplementation(() =>
    Promise.resolve([
      {
        id: 'appeal-1',
        status: 'pending',
        submittedAt: new Date().toISOString(),
        infractionId: 'inf-1',
        reason: 'Test appeal'
      }
    ])
  )
}));

describe('AppealSystem', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the appeal system components', () => {
    render(
      <AppealProvider>
        <AppealSystem playerId="player-1" />
      </AppealProvider>
    );

    expect(screen.getByText(/Submit Appeal/i)).toBeInTheDocument();
    expect(screen.getByText(/Active Appeals/i)).toBeInTheDocument();
  });

  it('loads and displays active appeals', async () => {
    render(
      <AppealProvider>
        <AppealSystem playerId="player-1" />
      </AppealProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Test appeal/i)).toBeInTheDocument();
      expect(screen.getByText(/pending/i)).toBeInTheDocument();
    });
  });
});

describe('AppealForm', () => {
  const mockSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('validates required fields', async () => {
    render(<AppealForm onSubmit={mockSubmit} infractionId="inf-1" />);

    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/reason is required/i)).toBeInTheDocument();
    });
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it('submits appeal with valid data', async () => {
    render(<AppealForm onSubmit={mockSubmit} infractionId="inf-1" />);

    const reasonInput = screen.getByLabelText(/reason/i);
    const evidenceInput = screen.getByLabelText(/evidence/i);
    
    await userEvent.type(reasonInput, 'This was a mistake');
    await userEvent.type(evidenceInput, 'Here is my evidence');

    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        infractionId: 'inf-1',
        reason: 'This was a mistake',
        evidence: 'Here is my evidence'
      });
    });
  });

  it('handles file attachments', async () => {
    render(<AppealForm onSubmit={mockSubmit} infractionId="inf-1" />);

    const file = new File(['screenshot content'], 'screenshot.png', { type: 'image/png' });
    const fileInput = screen.getByLabelText(/attach files/i);

    await userEvent.upload(fileInput, file);

    expect(screen.getByText(/screenshot.png/i)).toBeInTheDocument();
  });
});

describe('AppealStatus', () => {
  it('displays appeal status correctly', async () => {
    render(
      <AppealStatus
        appeal={{
          id: 'appeal-1',
          status: 'approved',
          submittedAt: new Date().toISOString(),
          response: 'Appeal approved based on evidence',
          processedAt: new Date().toISOString()
        }}
      />
    );

    expect(screen.getByText(/approved/i)).toBeInTheDocument();
    expect(screen.getByText(/Appeal approved based on evidence/i)).toBeInTheDocument();
  });

  it('shows pending state correctly', () => {
    render(
      <AppealStatus
        appeal={{
          id: 'appeal-1',
          status: 'pending',
          submittedAt: new Date().toISOString(),
          response: null,
          processedAt: null
        }}
      />
    );

    expect(screen.getByText(/pending review/i)).toBeInTheDocument();
    expect(screen.getByText(/submitted/i)).toBeInTheDocument();
  });

  it('displays rejection with reason', () => {
    render(
      <AppealStatus
        appeal={{
          id: 'appeal-1',
          status: 'rejected',
          submittedAt: new Date().toISOString(),
          response: 'Insufficient evidence provided',
          processedAt: new Date().toISOString()
        }}
      />
    );

    expect(screen.getByText(/rejected/i)).toBeInTheDocument();
    expect(screen.getByText(/Insufficient evidence provided/i)).toBeInTheDocument();
  });

  it('handles appeal updates', async () => {
    const { rerender } = render(
      <AppealStatus
        appeal={{
          id: 'appeal-1',
          status: 'pending',
          submittedAt: new Date().toISOString(),
          response: null,
          processedAt: null
        }}
      />
    );

    expect(screen.getByText(/pending review/i)).toBeInTheDocument();

    // Simulate appeal update
    rerender(
      <AppealStatus
        appeal={{
          id: 'appeal-1',
          status: 'approved',
          submittedAt: new Date().toISOString(),
          response: 'Appeal approved',
          processedAt: new Date().toISOString()
        }}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/approved/i)).toBeInTheDocument();
      expect(screen.getByText(/Appeal approved/i)).toBeInTheDocument();
    });
  });
}); 