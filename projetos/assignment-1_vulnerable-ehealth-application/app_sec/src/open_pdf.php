<?php
require_once('database/Database.php');
session_start();
unset($_SESSION['REFRESH1']);
unset($_SESSION['REFRESH2']);
unset($_SESSION['REFRESH3']);

include_once("./csrf_validate.php");
$app = new appointments();
if(!isset($_SESSION['userEmail'])) header("Location: index.php");

if(!empty($_GET['code']) && !empty($_GET['appointment_id']) && !empty($_GET['token'])){
    $code = strip_tags(trim($_GET['code']));
    $appointmentId = htmlspecialchars($_GET['appointment_id']);
    $token = htmlspecialchars($_GET['token']);
}else
    header("Location: ./info.php?type=4");

if(!validateInputs($appointmentId, 'int') || !check_valid_token($token)) header("Location: ./info.php?type=4");

$query = $app->select_using_code($code);

$row = $query->fetch_assoc();

if(!$row || $row['id'] != $appointmentId)
{
    header("Location: info.php?type=4");
}

$users = new users();
$patient = $users->select_by_id($row["client_id"])->fetch_assoc();
$doctor = $users->select_by_id($row["doctors_id"])->fetch_assoc();

if(($patient["email"] != $_SESSION['userEmail']) && ($doctor["email"] != $_SESSION['userEmail'])) header("Location: ./info.php?type=3");

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
$pdf->MultiCell(500,10 , "Speciality: ".htmlspecialchars($specname));
$pdf->MultiCell(500,10 , "Report code: ".htmlspecialchars($code));
$pdf->MultiCell(500,10 , "Patient name: ".htmlspecialchars($patient["first_name"])." ".htmlspecialchars($patient["last_name"]));
$pdf->MultiCell(500,10 , "Doctor name: ".htmlspecialchars($doctor["first_name"])." ".htmlspecialchars($doctor["last_name"]));
$pdf->MultiCell(500,10 , "Confirmed by doctor: ".htmlspecialchars($confirmed_str));
$pdf->MultiCell(500,10 , "Appointment finished: ".htmlspecialchars($done_str));
if($row["completed"])
{
    $pdf->MultiCell(500,10 , "Doctor report:".htmlspecialchars($row["report_text"]));
}
    
$pdf->Output('','test.pdf', false);



?>