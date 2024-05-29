import { Component } from '@angular/core';
import { DatePipe, formatDate } from '@angular/common';


@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.scss'
})
export class ContactComponent {
  public today= new Date();

}
