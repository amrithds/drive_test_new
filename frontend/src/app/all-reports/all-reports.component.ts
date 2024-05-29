import { Component } from '@angular/core';
import { FormBuilder,FormGroup } from '@angular/forms';
import { formatDate } from '@angular/common';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';


@Component({
  selector: 'app-all-reports',
  templateUrl: './all-reports.component.html',
  styleUrl: './all-reports.component.scss'
})
export class AllReportsComponent {
  public form!: FormGroup;
  public today= new Date();
  public all_reports:boolean=false;

  public center_content:any=[
    {
      "id":"A",
      "name":"STARTING POINT"
    },
    {
      "id":"B",
      "name":"ZIG ZAG TURN"
      },
    {
      "id":"C",
      "name":"SANDWICH PARKING"
    },
    {
      "id":"D",
      "name":"NARROW BRIDGE CROSSING"
    },
    {
      "id":"E",
      "name":"TUNNEL"
    },
    {
      "id":"F",
      "name":"UP & DOWN HILL"
    },
    {
      "id":"G",
      "name":"RAILWAY CROSSING"
    },
    {
      "id":"H",
      "name":"FIGURE OF H"
    },
    {
      "id":"I",
        "name":"U TURN"
    },
    {
      "id":"J",
      "name":"SAND PIT"
    },
    {
      "id":"K",
      "name":"FIGURE OF X"
    },
    {
      "id":"L",
      "name":"LEFT REVERSE PARKING"
    },
    {
      "id":"M",
      "name":"RIGHT REVERSE PARKING"
    },
    {
      "id":"N",
      "name":"FINISHING POINT"
    },
]


  constructor(private fb:FormBuilder){}

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
