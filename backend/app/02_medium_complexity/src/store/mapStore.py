from typing import Any, Dict, List, Union



  MapMarker as WSMapMarker,
  WebSocketMessage,
} from '../services/WebSocketService'
class MapMarker:
    id: str
    position: LatLng
    title: str
    description: str
class MapState:
    center: LatLng
    zoom: float
    markers: List[MapMarker]
    selectedMarkerId: Union[str, None]
    isConnected: bool
    setCenter: (center: LatLng) => None
    setZoom: (zoom: float) => None
    addMarker: (marker: Omit<MapMarker, 'id'>) => None
    updateMarker: (id: str, marker: Partial<Omit<MapMarker, 'id'>>) => None
    removeMarker: (id: str) => None
    setSelectedMarkerId: Union[(id: str, None) => None]
    setIsConnected: (isConnected: bool) => None
    initializeWebSocket: () => None
const convertToLatLng = (pos: Dict[str, Any]): LatLng => new LatLng(pos.lat, pos.lng)
const convertMarkerFromWS = (marker: WSMapMarker): \'MapMarker\' => ({
  ...marker,
  position: convertToLatLng(marker.position),
})
const convertMarkerToWS = (marker: MapMarker): WSMapMarker => ({
  ...marker,
  position: Dict[str, Any],
})
const useMapStore = create<MapState>()(
  persist(
    (set, get) => {
      const ws = WebSocketService.getInstance()
      const handleWebSocketMessage = (message: WebSocketMessage) => {
        switch (message.type) {
          case 'state':
            set({
              markers: message.data.markers.map(convertMarkerFromWS),
              center: convertToLatLng(message.data.center),
              zoom: message.data.zoom,
            })
            break
          case 'marker_add':
            set(state => ({
              markers: [...state.markers, convertMarkerFromWS(message.data)],
            }))
            break
          case 'marker_update':
            set(state => ({
              markers: state.markers.map(m =>
                m.id === message.data.id ? convertMarkerFromWS(message.data) : m
              ),
            }))
            break
          case 'marker_remove':
            set(state => ({
              markers: state.markers.filter(m => m.id !== message.data.id),
              selectedMarkerId:
                state.selectedMarkerId === message.data.id ? null : state.selectedMarkerId,
            }))
            break
          case 'view_update':
            set({
              center: convertToLatLng(message.data.center),
              zoom: message.data.zoom,
            })
            break
        }
      }
      return {
        center: new LatLng(51.505, -0.09), 
        zoom: 13,
        markers: [],
        selectedMarkerId: null,
        isConnected: false,
        setCenter: (center: LatLng) => {
          set({ center })
          ws.updateView(center, get().zoom)
        },
        setZoom: (zoom: float) => {
          set({ zoom })
          ws.updateView(get().center, zoom)
        },
        addMarker: (marker: Omit<MapMarker, 'id'>) => {
          const newMarker = {
            ...marker,
            id: Math.random().toString(36).substr(2, 9),
          }
          ws.addMarker(convertMarkerToWS(newMarker))
        },
        updateMarker: (id: str, marker: Partial<Omit<MapMarker, 'id'>>) => {
          const state = get()
          const existingMarker = state.markers.find(m => m.id === id)
          if (existingMarker) {
            const updatedMarker = { ...existingMarker, ...marker }
            ws.updateMarker(convertMarkerToWS(updatedMarker))
          }
        },
        removeMarker: (id: str) => {
          ws.removeMarker(id)
        },
        setSelectedMarkerId: (id: str | null) => set({ selectedMarkerId: id }),
        setIsConnected: (isConnected: bool) => set({ isConnected }),
        initializeWebSocket: () => {
          ws.addMessageHandler(handleWebSocketMessage)
          ws.connect()
        },
      }
    },
    {
      name: 'map-storage',
      partialize: state => ({
        center: Dict[str, Any],
        zoom: state.zoom,
        selectedMarkerId: state.selectedMarkerId,
      }),
      onRehydrateStorage: () => state => {
        if (state) {
          state.center = new LatLng(state.center.lat, state.center.lng)
          state.initializeWebSocket()
        }
      },
    }
  )
)