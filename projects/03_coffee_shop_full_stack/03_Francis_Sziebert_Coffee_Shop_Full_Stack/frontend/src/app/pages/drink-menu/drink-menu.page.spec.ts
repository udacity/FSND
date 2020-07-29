import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DrinkMenuPage } from './drink-menu.page';

describe('DrinkMenuPage', () => {
  let component: DrinkMenuPage;
  let fixture: ComponentFixture<DrinkMenuPage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DrinkMenuPage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DrinkMenuPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
