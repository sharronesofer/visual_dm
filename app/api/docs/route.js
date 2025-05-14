import { createSwaggerSpec } from 'next-swagger-doc';
import { NextResponse } from 'next/server';
import swaggerConfig from '../../../swagger.config';

export async function GET() {
  const spec = createSwaggerSpec({
    definition: swaggerConfig,
  });

  return NextResponse.json(spec);
} 