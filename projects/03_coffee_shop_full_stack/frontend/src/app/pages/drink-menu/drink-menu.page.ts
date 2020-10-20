import { Component, OnInit } from '@angular/core';
import { DrinksService, Drink } from '../../services/drinks.service';
import { ModalController } from '@ionic/angular';
import { DrinkFormComponent } from './drink-form/drink-form.component';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-drink-menu',
  templateUrl: './drink-menu.page.html',
  styleUrls: ['./drink-menu.page.scss'],
})
export class DrinkMenuPage implements OnInit {
  Object = Object;

  constructor(
    private auth: AuthService,
    private modalCtrl: ModalController,
    public drinks: DrinksService
    ) { }

  ngOnInit() {
    this.drinks.getDrinks();
  }

  async openForm(activedrink: Drink = null) {
    if (!this.auth.can('get:drinks-detail')) {
      return;
    }

    const modal = await this.modalCtrl.create({
      component: DrinkFormComponent,
      componentProps: { drink: activedrink, isNew: !activedrink }
    });

    modal.present();
  }

}
