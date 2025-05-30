from typing import Any


const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
      ])
    )
  }),
  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params
    if (id === '1') {
      return res(
        ctx.status(200),
        ctx.json({ id: 1, name: 'John Doe', email: 'john@example.com' })
      )
    }
    return res(ctx.status(404))
  }),
  rest.post('/api/users', async (req, res, ctx) => {
    const body = await req.json()
    if (!body.name || !body.email) {
      return res(
        ctx.status(400),
        ctx.json({ message: 'Name and email are required' })
      )
    }
    return res(
      ctx.status(201),
      ctx.json({ id: 3, ...body })
    )
  }),
  rest.put('/api/users/:id', async (req, res, ctx) => {
    const { id } = req.params
    const body = await req.json()
    if (id === '1') {
      return res(
        ctx.status(200),
        ctx.json({ id: 1, ...body })
      )
    }
    return res(ctx.status(404))
  }),
  rest.delete('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params
    if (id === '1') {
      return res(ctx.status(204))
    }
    return res(ctx.status(404))
  })
)
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())