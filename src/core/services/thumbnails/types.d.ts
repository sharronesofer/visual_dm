declare module 'pdf2pic' {
  interface ConversionOptions {
    density?: number;
    saveFilename?: string;
    savePath?: string;
    format?: string;
    width?: number;
    height?: number;
  }

  interface ConversionResult {
    name?: string;
    path?: string;
    size?: number;
    page?: number;
    base64?: string;
  }

  interface PDF2Pic {
    (page: number): Promise<ConversionResult>;
    bulk: (pages: number[], savePath: string) => Promise<ConversionResult[]>;
  }

  interface PDF2PicStatic {
    fromPath: (path: string, options?: ConversionOptions) => PDF2Pic;
    fromBuffer: (buffer: Buffer, options?: ConversionOptions) => PDF2Pic;
  }

  const pdf2pic: PDF2PicStatic;
  export = pdf2pic;
} 