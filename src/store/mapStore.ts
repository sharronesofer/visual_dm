import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { LatLng } from 'leaflet';
import WebSocketService, {
  MapMarker as WSMapMarker,
  WebSocketMessage,
} from '../services/WebSocketService';

interface MapMarker {
  id: string;
  position: LatLng;
  title: string;
  description: string;
}

interface MapState {
  center: LatLng;
  zoom: number;
  markers: MapMarker[];
  selectedMarkerId: string | null;
  isConnected: boolean;
  setCenter: (center: LatLng) => void;
  setZoom: (zoom: number) => void;
  addMarker: (marker: Omit<MapMarker, 'id'>) => void;
  updateMarker: (id: string, marker: Partial<Omit<MapMarker, 'id'>>) => void;
  removeMarker: (id: string) => void;
  setSelectedMarkerId: (id: string | null) => void;
  setIsConnected: (isConnected: boolean) => void;
  initializeWebSocket: () => void;
}

const convertToLatLng = (pos: { lat: number; lng: number }): LatLng => new LatLng(pos.lat, pos.lng);

const convertMarkerFromWS = (marker: WSMapMarker): MapMarker => ({
  ...marker,
  position: convertToLatLng(marker.position),
});

const convertMarkerToWS = (marker: MapMarker): WSMapMarker => ({
  ...marker,
  position: { lat: marker.position.lat, lng: marker.position.lng },
});

export const useMapStore = create<MapState>()(
  persist(
    (set, get) => {
      // Initialize WebSocket connection
      const ws = WebSocketService.getInstance();

      const handleWebSocketMessage = (message: WebSocketMessage) => {
        switch (message.type) {
          case 'state':
            set({
              markers: message.data.markers.map(convertMarkerFromWS),
              center: convertToLatLng(message.data.center),
              zoom: message.data.zoom,
            });
            break;
          case 'marker_add':
            set(state => ({
              markers: [...state.markers, convertMarkerFromWS(message.data)],
            }));
            break;
          case 'marker_update':
            set(state => ({
              markers: state.markers.map(m =>
                m.id === message.data.id ? convertMarkerFromWS(message.data) : m
              ),
            }));
            break;
          case 'marker_remove':
            set(state => ({
              markers: state.markers.filter(m => m.id !== message.data.id),
              selectedMarkerId:
                state.selectedMarkerId === message.data.id ? null : state.selectedMarkerId,
            }));
            break;
          case 'view_update':
            set({
              center: convertToLatLng(message.data.center),
              zoom: message.data.zoom,
            });
            break;
        }
      };

      return {
        center: new LatLng(51.505, -0.09), // London
        zoom: 13,
        markers: [],
        selectedMarkerId: null,
        isConnected: false,

        setCenter: (center: LatLng) => {
          set({ center });
          ws.updateView(center, get().zoom);
        },

        setZoom: (zoom: number) => {
          set({ zoom });
          ws.updateView(get().center, zoom);
        },

        addMarker: (marker: Omit<MapMarker, 'id'>) => {
          const newMarker = {
            ...marker,
            id: Math.random().toString(36).substr(2, 9),
          };
          ws.addMarker(convertMarkerToWS(newMarker));
        },

        updateMarker: (id: string, marker: Partial<Omit<MapMarker, 'id'>>) => {
          const state = get();
          const existingMarker = state.markers.find(m => m.id === id);
          if (existingMarker) {
            const updatedMarker = { ...existingMarker, ...marker };
            ws.updateMarker(convertMarkerToWS(updatedMarker));
          }
        },

        removeMarker: (id: string) => {
          ws.removeMarker(id);
        },

        setSelectedMarkerId: (id: string | null) => set({ selectedMarkerId: id }),

        setIsConnected: (isConnected: boolean) => set({ isConnected }),

        initializeWebSocket: () => {
          ws.addMessageHandler(handleWebSocketMessage);
          ws.connect();
        },
      };
    },
    {
      name: 'map-storage',
      partialize: state => ({
        center: { lat: state.center.lat, lng: state.center.lng },
        zoom: state.zoom,
        selectedMarkerId: state.selectedMarkerId,
      }),
      onRehydrateStorage: () => state => {
        if (state) {
          state.center = new LatLng(state.center.lat, state.center.lng);
          // Initialize WebSocket connection after rehydration
          state.initializeWebSocket();
        }
      },
    }
  )
);
