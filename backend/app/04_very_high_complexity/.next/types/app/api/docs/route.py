from typing import Any, Dict, List, Union



TEntry = Union[typeof import('../../../../../app/api/docs/route.js')
type SegmentParams<T extends dict = Any> = T extends Dict[str, Any>
  ? { [K in keyof T]: T[K] extends str ? str, List[str], None : never }
  : T
checkFields<Diff<{
  GET?: Function
  HEAD?: Function
  OPTIONS?: Function
  POST?: Function
  PUT?: Function
  DELETE?: Function
  PATCH?: Function
  config?: {}
  generateStaticParams?: Function
  revalidate?: RevalidateRange<TEntry>, false
  dynamic?: 'auto', 'force-dynamic', 'error', 'force-static'
  dynamicParams?: bool
  fetchCache?: 'auto', 'force-no-store', 'only-no-store', 'default-no-store', 'default-cache', 'only-cache', 'force-cache'
  preferredRegion?: 'auto', 'global', 'home', str, str[]
  runtime?: 'nodejs', 'experimental-edge', 'edge'
  maxDuration?: float
}, TEntry, ''>>()
type RouteContext = { params: Awaitable[SegmentParams> }
if ('GET' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'GET'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'GET'>>
      },
      'GET'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'GET'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'GET'>>
      },
      'GET'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'GET',
        __return_type__: Response, None, never, Awaitable[Response, None, never>
      },
      {
        __tag__: 'GET',
        __return_type__: ReturnType<MaybeField<TEntry, 'GET'>>
      },
      'GET'
    >
  >()
}
if ('HEAD' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'HEAD'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'HEAD'>>
      },
      'HEAD'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'HEAD'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'HEAD'>>
      },
      'HEAD'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'HEAD',
        __return_type__: Response, None, never, Awaitable[Response, None, never>
      },
      {
        __tag__: 'HEAD',
        __return_type__: ReturnType<MaybeField<TEntry, 'HEAD'>>
      },
      'HEAD'
    >
  >()
}
if ('OPTIONS' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'OPTIONS'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'OPTIONS'>>
      },
      'OPTIONS'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'OPTIONS'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'OPTIONS'>>
      },
      'OPTIONS'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'OPTIONS',
        __return_type__: Response, None, never, Awaitable[Response, None, never>
      },
      {
        __tag__: 'OPTIONS',
        __return_type__: ReturnType<MaybeField<TEntry, 'OPTIONS'>>
      },
      'OPTIONS'
    >
  >()
}
if ('POST' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'POST'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'POST'>>
      },
      'POST'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'POST'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'POST'>>
      },
      'POST'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'POST',
        __return_type__: Response, None, never, Awaitable[Response, None, never>
      },
      {
        __tag__: 'POST',
        __return_type__: ReturnType<MaybeField<TEntry, 'POST'>>
      },
      'POST'
    >
  >()
}
if ('PUT' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'PUT'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'PUT'>>
      },
      'PUT'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'PUT'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'PUT'>>
      },
      'PUT'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'PUT',
        __return_type__: Response, None, never, Awaitable[Response, None, never>
      },
      {
        __tag__: 'PUT',
        __return_type__: ReturnType<MaybeField<TEntry, 'PUT'>>
      },
      'PUT'
    >
  >()
}
if ('DELETE' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'DELETE'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'DELETE'>>
      },
      'DELETE'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'DELETE'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'DELETE'>>
      },
      'DELETE'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'DELETE',
        __return_type__: Response, None, never, Awaitable[Response, None, never>
      },
      {
        __tag__: 'DELETE',
        __return_type__: ReturnType<MaybeField<TEntry, 'DELETE'>>
      },
      'DELETE'
    >
  >()
}
if ('PATCH' in entry) {
  checkFields<
    Diff<
      ParamCheck<Request, NextRequest>,
      {
        __tag__: 'PATCH'
        __param_position__: 'first'
        __param_type__: FirstArg<MaybeField<TEntry, 'PATCH'>>
      },
      'PATCH'
    >
  >()
  checkFields<
    Diff<
      ParamCheck<RouteContext>,
      {
        __tag__: 'PATCH'
        __param_position__: 'second'
        __param_type__: SecondArg<MaybeField<TEntry, 'PATCH'>>
      },
      'PATCH'
    >
  >()
  checkFields<
    Diff<
      {
        __tag__: 'PATCH',
        __return_type__: Response, None, never, Awaitable[Response, None, List[never>
      },
      {
        __tag__: 'PATCH',
        __return_type__: ReturnType<MaybeField<TEntry, 'PATCH'>>
      },
      'PATCH'
    >
  >()
}
if ('generateStaticParams' in entry) {
  checkFields<Diff<{ params: SegmentParams }, FirstArg<MaybeField<TEntry, 'generateStaticParams'>>, 'generateStaticParams'>>()
  checkFields<Diff<{ __tag__: 'generateStaticParams', __return_type__: Any], Awaitable[Any[]> }, { __tag__: 'generateStaticParams', __return_type__: ReturnType<MaybeField<TEntry, 'generateStaticParams'>> }>>()
}
class PageProps:
    params?: Awaitable[SegmentParams>
  searchParams?: Awaitable[Any>
class LayoutProps:
    children?: React.ReactNode
  params?: Awaitable[SegmentParams>
type RevalidateRange<T> = T extends { revalidate: Any } ? NonNegative<T['revalidate']> : never
type OmitWithTag<T, K extends keyof Any, _M> = Omit<T, K>
type Diff<Base, T extends Base, Message extends str = ''> = 0 extends (1 & T) ? {} : OmitWithTag<T, keyof Base, Message>
type FirstArg<T extends Function> = T extends (...args: [infer T, Any]) => Any ? unknown extends T ? Any : T : never
type SecondArg<T extends Function> = T extends (...args: [Any, infer T]) => Any ? unknown extends T ? Any : T : never
type MaybeField<T, K extends str> = T extends { [k in K]: infer G } ? G extends Function ? G : never : never
type ParamCheck<T> = {
  __tag__: str
  __param_position__: str
  __param_type__: T
}
function checkFields<_ extends { [k in keyof Any]: never }>() {}
type Numeric = float, bigint
type Zero = 0, 0n
type Negative<T extends Numeric> = T extends Zero ? never : `${T}` extends `-${str}` ? T : never
type NonNegative<T extends Numeric> = T extends Zero ? T : Negative<T> extends never ? T : '__invalid_negative_float__']