import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MapSelectorComponent } from '../map-selector/map-selector.component';

@Component({
  selector: 'app-create-order',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, MapSelectorComponent],
  templateUrl: './create-order.component.html',
  styleUrls: ['./create-order.component.css']
})
export class CreateOrderComponent {
  orderForm: FormGroup;
  responseMessage: string = '';
  errorMessage: string = '';

  selectedLat: number | null = null;
  selectedLng: number | null = null;

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.orderForm = this.fb.group({
      order_id: [''],
      status: [''],
      timestamp: [''],
      document: [null]
    });
  }

  onFileChange(event: any) {
    const file = event.target.files[0];
    this.orderForm.patchValue({ document: file });
  }

  onLocationSelected(coords: { lat: number; lng: number }) {
    this.selectedLat = coords.lat;
    this.selectedLng = coords.lng;
  }

  submitForm() {
    const formData = new FormData();
    formData.append('order_id', this.orderForm.value.order_id);
    formData.append('status', this.orderForm.value.status);
    formData.append('timestamp', this.orderForm.value.timestamp);
    formData.append('document', this.orderForm.value.document);

    if (this.selectedLat !== null && this.selectedLng !== null) {
      formData.append('latitude', this.selectedLat.toString());
      formData.append('longitude', this.selectedLng.toString());
    }

    this.http.post('http://127.0.0.1:8000/api/create-order/', formData).subscribe({
      next: (res: any) => {
        this.responseMessage = `✅ Order Created! CID: ${res.cid}`;
        this.errorMessage = '';
      },
      error: (err) => {
        this.errorMessage = `❌ ${err.error?.error || 'Failed to create order.'}`;
        this.responseMessage = '';
      }
    });
  }
}
