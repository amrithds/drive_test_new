import { Directive, HostListener } from '@angular/core';

@Directive({
  selector: '[appPreventEnterButton]'
})
export class PreventEnterButtonDirective {

  constructor() { }

  @HostListener('keydown', ['$event'])
  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      event.stopPropagation();
    }
  }

}
