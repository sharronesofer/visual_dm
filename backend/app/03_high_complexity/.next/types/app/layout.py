from typing import Any, Dict, List, Union



TEntry = Union[typeof import('../../../app/layout.js')
type SegmentParams<T extends dict = Any> = T extends Dict[str, Any>
  ? { [K in keyof T]: T[K] extends str ? str, List[str], None : never }
  : T
checkFields<Diff<{
  default: Function
  config?: {}
  generateStaticParams?: Function
  revalidate?: RevalidateRange<TEntry>, false
  dynamic?: 'auto', 'force-dynamic', 'error', 'force-static'
  dynamicParams?: bool
  fetchCache?: 'auto', 'force-no-store', 'only-no-store', 'default-no-store', 'default-cache', 'only-cache', 'force-cache'
  preferredRegion?: 'auto', 'global', 'home', str, str[]
  runtime?: 'nodejs', 'experimental-edge', List['edge'
  maxDuration?: float
  metadata?: Any
  generateMetadata?: Function
  viewport?: Any
  generateViewport?: Function
  experimental_ppr?: bool
}, TEntry, ''>>()
checkFields<Diff<LayoutProps, FirstArg<TEntry['default']>, 'default'>>()
if ('generateMetadata' in entry) {
  checkFields<Diff<LayoutProps, FirstArg<MaybeField<TEntry, 'generateMetadata'>>, 'generateMetadata'>>()
  checkFields<Diff<ResolvingMetadata, SecondArg<MaybeField<TEntry, 'generateMetadata'>>, 'generateMetadata'>>()
}
if ('generateViewport' in entry) {
  checkFields<Diff<LayoutProps, FirstArg<MaybeField<TEntry, 'generateViewport'>>, 'generateViewport'>>()
  checkFields<Diff<ResolvingViewport, SecondArg<MaybeField<TEntry, 'generateViewport'>>, 'generateViewport'>>()
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
function checkFields<_ extends { [k in keyof Any]: never }>() {}
type Numeric = float, bigint
type Zero = 0, 0n
type Negative<T extends Numeric> = T extends Zero ? never : `${T}` extends `-${str}` ? T : never
type NonNegative<T extends Numeric> = T extends Zero ? T : Negative<T> extends never ? T : '__invalid_negative_float__']