<?php
require_once('database/Database.php');
$app = new appointments();
$code = $_GET["code"];
$query = $app->select_using_code($code);

$row = $query->fetch_assoc();

if(!$row)
{
    header("Location: info.php?type=4");
}

$users = new users();
$patient = $users->select_by_id($row["client_id"])->fetch_assoc();
$doctor = $users->select_by_id($row["doctors_id"])->fetch_assoc();

$speciality = new specialties_doctors();
$specid = $speciality->select_by_doctors_id($doctor["id"])->fetch_assoc()["specialties_id"];
$specnames = new specialties();
$specname = $specnames->select_by_id($specid)->fetch_assoc()["name"];

$confirmed_str = ($row["confirmed"]) ? 'yes' : 'no';
$done_str = ($row["completed"]) ? 'yes' : 'no';

require('FPDF/fpdf.php');
$pdf = new FPDF();
$pdf->AddPage();
$pdf->SetFont('Arial','B',16);
$pdf->Cell(80 , 10 , "Thrine");
$pdf->MultiCell(40 , 10 , "Appointment");
$pdf->MultiCell(500,10 , "Speciality: ".$specname);
$pdf->MultiCell(500,10 , "Report code: ".$code);
$pdf->MultiCell(500,10 , "Patient name: ".$patient["first_name"]." ".$patient["last_name"]);
$pdf->MultiCell(500,10 , "Doctor name: ".$doctor["first_name"]." ".$doctor["last_name"]);
$pdf->MultiCell(500,10 , "Confirmed by doctor: ".$confirmed_str);
$pdf->MultiCell(500,10 , "Appointment finished: ".$done_str);
if($row["completed"])
{
    $pdf->MultiCell(500,10 , "Doctor report:".$row["report_text"]);
}
    
$pdf->Output('','test.pdf', false);



?>