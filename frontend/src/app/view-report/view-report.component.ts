
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DatePipe, formatDate } from '@angular/common';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment/environment';


@Component({
  selector: 'app-view-report',
  templateUrl: './view-report.component.html',
  styleUrls: ['./view-report.component.scss'],
  providers: [DatePipe]
})
export class ViewReportComponent {
  public form!: FormGroup;
  public today = new Date();
  public getDatetime = '';
  public enabletable: boolean = false;
  public enablereport: boolean = false;
  public showpdf: boolean = false;
  public environment=environment;
  public individual_report:any=[];


  constructor(
    private fb: FormBuilder,
    private http: HttpClient,

  ) {
    this.getDatetime = formatDate(this.today, 'dd-MM-yyyy hh:mm a', 'en-US', '+0530');
  }

  ngOnInit() {
    this.form = this.fb.group({
      trainee_id: [null,Validators.required],
    });
  }

  getreports() {
    this.http.get(this.environment.apiUrl + 'v1/course/session/?search='+this.form.value['trainee_id']).subscribe(
      (data: any) => {
        console.log(data.results)
        this.individual_report = data.results
        if(this.individual_report.length>0){
          this.enabletable = true;
        }else{
          window.alert("Trainee not exist")
        }
      },
      (error: any) => {
        console.error('Error fetching data:', error);
      }
    );  
  }
  public view_report:any;
  viewReport(index:any){
    this.enablereport=true;
    this.enabletable=false;
    console.log(index)
    this.view_report = this.individual_report[index]
    console.log(this.view_report)
  }

  generatePDF() {
    const data = document.getElementById('reportContent')!;
    console.log(data)
    html2canvas(data).then(canvas => {
      const imgWidth = 210;
      const imgHeight = canvas.height * imgWidth / canvas.width;

      const contentDataURL = canvas.toDataURL('image/png');
      let pdf = new jsPDF('p', 'mm', 'a4');
      const position = 0;
      pdf.addImage(contentDataURL, 'PNG', 0, position, imgWidth, imgHeight);

       // Add footer
      pdf.setFontSize(10);
       pdf.text('Smart Skill Driving Technology By | FIRSTSERVE.com | Mob:99000 99100', 50, pdf.internal.pageSize.height - 10); 

      // Open the PDF in a new tab and trigger the print dialog
      const pdfOutput = pdf.output('blob');
      const blobUrl = URL.createObjectURL(pdfOutput);
      
      const printWindow = window.open(blobUrl);
    });
  }

}
