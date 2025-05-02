import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReadOrderComponent } from './read-order.component';

describe('ReadOrderComponent', () => {
  let component: ReadOrderComponent;
  let fixture: ComponentFixture<ReadOrderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReadOrderComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReadOrderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
