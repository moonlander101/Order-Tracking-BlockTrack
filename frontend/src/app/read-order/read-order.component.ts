// src/app/read-order/read-order.component.ts
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-read-order',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './read-order.component.html'
})
export class ReadOrderComponent {
  readForm: FormGroup;
  result: any = null;
  loading = false;

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.readForm = this.fb.group({
      order_id: ['', Validators.required]
    });
  }

  submitForm() {
    if (this.readForm.invalid) return;
    const orderId = this.readForm.value.order_id;
    this.loading = true;
    this.result = null;

    this.http.get(`http://127.0.0.1:8000/api/read-order/${orderId}/`).subscribe({
      next: (res) => {
        this.result = res;
        this.loading = false;
      },
      error: (err) => {
        this.result = err.error || { error: 'Request failed' };
        this.loading = false;
      }
    });
  }
}
