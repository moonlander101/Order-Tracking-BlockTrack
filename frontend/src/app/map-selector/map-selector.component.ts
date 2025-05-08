import { Component, ElementRef, ViewChild, AfterViewInit, Output, EventEmitter } from '@angular/core';
import * as L from 'leaflet';
//import 'leaflet/dist/images/marker-icon.png';
//import 'leaflet/dist/images/marker-shadow.png';

// Fix Leaflet marker icon paths
delete (L.Icon.Default.prototype as any)._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'assets/marker-icon-2x.png',
  iconUrl: 'assets/marker-icon.png',
  shadowUrl: 'assets/marker-shadow.png',
});


@Component({
  selector: 'app-map-selector',
  standalone: true,
  imports: [],
  templateUrl: './map-selector.component.html',
  styleUrls: ['./map-selector.component.css']
})
export class MapSelectorComponent implements AfterViewInit {
  @ViewChild('mapDiv') mapDiv!: ElementRef;

  @Output() locationSelected = new EventEmitter<{ lat: number; lng: number }>();

  map!: L.Map;
  marker!: L.Marker;
  lat = 7.8731;
  lng = 80.7718;

  ngAfterViewInit(): void {
    this.map = L.map(this.mapDiv.nativeElement).setView([this.lat, this.lng], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    this.map.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;

      if (this.marker) {
        this.map.removeLayer(this.marker);
      }

      this.marker = L.marker([lat, lng]).addTo(this.map);
      this.lat = lat;
      this.lng = lng;

      // 🔥 Emit the selected coordinates
      this.locationSelected.emit({ lat, lng });
    });
  }
}
