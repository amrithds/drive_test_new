import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TrainingComponent } from './training/training.component';
import { ViewReportComponent } from './view-report/view-report.component';
import { AllReportsComponent } from './all-reports/all-reports.component';
import { AddUserComponent } from './add-user/add-user.component';
import { ContactComponent } from './contact/contact.component';
import { LoginComponent } from './login/login.component';
import { LiveDashboardComponent } from './live-dashboard/live-dashboard.component';
import { AuthGuard } from './auth.guard';

const routes: Routes = [
  {
    path:'',
    component:LoginComponent
  },
  {
    path:'training',
    component:TrainingComponent,
    canActivate: [AuthGuard]
  },
  {
    path:'view_report',
    component:ViewReportComponent
  },
  {
    path:'all_reports',
    component:AllReportsComponent
  },
  {
    path:'add_user',
    component:AddUserComponent
  },
  {
    path:'contact',
    component:ContactComponent
  },
  {
    path:'live',
    component:LiveDashboardComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
