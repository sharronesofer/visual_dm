import React from 'react';
import { render, generateTestId } from '../utils/test-utils';
import Button from '@/components/Button';

describe('Button', () => {
  it('renders with default props', () => {
    const { getByRole } = render(<Button>Click me</Button>);
    const button = getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Click me');
  });

  it('applies custom className', () => {
    const { getByRole } = render(
      <Button className="custom-class">Click me</Button>
    );
    const button = getByRole('button');
    expect(button).toHaveClass('custom-class');
  });

  it('handles click events', async () => {
    const handleClick = jest.fn();
    const { getByRole, user } = render(
      <Button onClick={handleClick}>Click me</Button>
    );
    const button = getByRole('button');
    
    await user.click(button);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('can be disabled', () => {
    const handleClick = jest.fn();
    const { getByRole } = render(
      <Button disabled onClick={handleClick}>
        Click me
      </Button>
    );
    const button = getByRole('button');
    
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('disabled');
  });

  it('renders with different variants', () => {
    const { getByTestId } = render(
      <Button variant="primary" data-testid={generateTestId('button', 'primary')}>
        Primary Button
      </Button>
    );
    const button = getByTestId('button-primary');
    expect(button).toHaveClass('btn-primary');
  });

  it('renders with loading state', () => {
    const { getByRole, getByTestId } = render(
      <Button loading data-testid={generateTestId('button', 'loading')}>
        Loading Button
      </Button>
    );
    const button = getByRole('button');
    const spinner = getByTestId('button-loading-spinner');
    
    expect(button).toBeDisabled();
    expect(spinner).toBeInTheDocument();
    expect(button).toHaveTextContent('Loading...');
  });

  it('renders with icon', () => {
    const { getByTestId } = render(
      <Button
        icon={<span data-testid="test-icon">🔍</span>}
        data-testid={generateTestId('button', 'icon')}
      >
        Search
      </Button>
    );
    const icon = getByTestId('test-icon');
    expect(icon).toBeInTheDocument();
  });

  it('applies size classes correctly', () => {
    const { getByRole } = render(
      <Button size="large">Large Button</Button>
    );
    const button = getByRole('button');
    expect(button).toHaveClass('btn-large');
  });
}); 