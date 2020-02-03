import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-user-page',
  templateUrl: './user-page.page.html',
  styleUrls: ['./user-page.page.scss'],
})
export class UserPagePage implements OnInit {
  loginURL: string;

  constructor(public auth: AuthService) {
    this.loginURL = auth.build_login_link('/tabs/user-page');
  }

  ngOnInit() {
  }

}
