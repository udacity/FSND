import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { AuthService } from './auth.service';
import { environment } from 'src/environments/environment';

export interface Drink {
  id: number;
  title: string;
  recipe: Array<{
          name: string,
          color: string,
          parts: number
        }>;
}

@Injectable({
  providedIn: 'root'
})
export class DrinksService {

  url = environment.apiServerUrl;

  public items: {[key: number]: Drink} = {};
  // = {
  //                             1: {
  //                             id: 1,
  //                             title: 'matcha shake',
  //                             recipe: [
  //                                   {
  //                                     name: 'milk',
  //                                     color: 'grey',
  //                                     parts: 1
  //                                   },
  //                                   {
  //                                     name: 'matcha',
  //                                     color: 'green',
  //                                     parts: 3
  //                                   },
  //                                 ]
  //                           },
  //                           2: {
  //                             id: 2,
  //                             title: 'flatwhite',
  //                             recipe: [

  //                                   {
  //                                     name: 'milk',
  //                                     color: 'grey',
  //                                     parts: 3
  //                                   },
  //                                   {
  //                                     name: 'coffee',
  //                                     color: 'brown',
  //                                     parts: 1
  //                                   },
  //                                 ]
  //                           },
  //                           3: {
  //                             id: 3,
  //                             title: 'cap',
  //                             recipe: [
  //                                   {
  //                                     name: 'foam',
  //                                     color: 'white',
  //                                     parts: 1
  //                                   },
  //                                   {
  //                                     name: 'milk',
  //                                     color: 'grey',
  //                                     parts: 2
  //                                   },
  //                                   {
  //                                     name: 'coffee',
  //                                     color: 'brown',
  //                                     parts: 1
  //                                   },
  //                                 ]
  //                           }
  //   };


  constructor(private auth: AuthService, private http: HttpClient) { }

  getHeaders() {
    const header = {
      headers: new HttpHeaders()
        .set('Authorization',  `Bearer ${this.auth.activeJWT()}`)
    };
    return header;
  }

  getDrinks() {
    if (this.auth.can('get:drinks-detail')) {
      this.http.get(this.url + '/drinks-detail', this.getHeaders())
      .subscribe((res: any) => {
        this.drinksToItems(res.drinks);
        console.log(res);
      });
    } else {
      this.http.get(this.url + '/drinks', this.getHeaders())
      .subscribe((res: any) => {
        this.drinksToItems(res.drinks);
        console.log(res);
      });
    }

  }

  saveDrink(drink: Drink) {
    if (drink.id >= 0) { // patch
      this.http.patch(this.url + '/drinks/' + drink.id, drink, this.getHeaders())
      .subscribe( (res: any) => {
        if (res.success) {
          this.drinksToItems(res.drinks);
        }
      });
    } else { // insert
      this.http.post(this.url + '/drinks', drink, this.getHeaders())
      .subscribe( (res: any) => {
        if (res.success) {
          this.drinksToItems(res.drinks);
        }
      });
    }

  }

  deleteDrink(drink: Drink) {
    delete this.items[drink.id];
    this.http.delete(this.url + '/drinks/' + drink.id, this.getHeaders())
    .subscribe( (res: any) => {

    });
  }

  drinksToItems( drinks: Array<Drink>) {
    for (const drink of drinks) {
      this.items[drink.id] = drink;
    }
  }
}
