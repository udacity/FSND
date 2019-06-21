import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UserPagePage } from './user-page.page';

describe('UserPagePage', () => {
  let component: UserPagePage;
  let fixture: ComponentFixture<UserPagePage>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UserPagePage ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UserPagePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
