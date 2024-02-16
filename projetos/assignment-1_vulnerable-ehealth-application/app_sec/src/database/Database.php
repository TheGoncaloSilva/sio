<?php
function generateRandomString($length = 12) {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $charactersLength = strlen($characters);
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, $charactersLength - 1)];
    }
    return $randomString;
}

class Database{
    public $conn;

    function __construct() {
        $this->conn = $this->create_connection();
    }

    function __destruct() {
        $this->close_connection();
    }

    public function getconn(){
        return $this->conn;
    }

    private function create_connection(){
        $server='mysql_db';
        $user='root';
        $password='easyPass123';
        $db='SIO';
        
        $conn = @mysqli_connect($server, $user, $password, $db) or die("A problem occurred while connecting to database, please go to reset.php page");
        /* check connection */
        if (!$conn) {
            //echo $e->getMessage();
            // $conn->connect_errno
            //echo "Failed to connect to MySQL database: (" . $conn->connect_errno . ") " . $conn->connect_error;
            header("Location: info.php?type=3");
            //die();
        }

        return $conn;
    }

    public function make_query($query){
        $res = $query->execute();
        if(!$res){ // query wasn't executed
            $query->close();
            return false;
        }
        $res = $query->get_result();
        if(!$res){ // Query was exectued is a insert, or a object that doens't return value
            $query->close();
            return true;
        }else{ // Query returns a value
            $query->close();
            return $res;
        }
        
        
    }

    private function close_connection(){
        if(!(($this->conn)->connect_errno)) mysqli_close($this->conn);
    }

}

/* Example Usage:
    $user = new users();
    $user->create('test', 'test', 'test@ua.pt', 'password', 1);
*/

class users extends Database{

    function __construct() {
        parent::__construct();
    }

    function create($firstName, $lastName, $email, $password, $roleId)
    {
        $query = ($this->conn)->prepare("INSERT INTO users(first_name,last_name,email,password,role) VALUES(?,?,?,?,?);");
        $query->bind_param('ssssi', $firstName, $lastName, $email, $password, $roleId);
        return $this->make_query($query);
    }
    
    function delete_using_email($email){
        $query = "DELETE FROM users WHERE email ='".$email."'";
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = ($this->conn)->prepare("DELETE FROM users WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM users;");
        return $this->make_query($query);
    }

    function update_using_email($email, $firstName, $lastName, $roleId){
        $query = ($this->conn)->prepare("UPDATE users SET first_name = ?, last_name = ?, role = ? WHERE email = ?;");
        $query->bind_param('ssis', $firstName, $lastName, $roleId, $email);
        return $this->make_query($query);
    }

    function update_using_id($id, $firstName, $lastName, $roleId){
        $query = ($this->conn)->prepare("UPDATE users SET first_name = ?, last_name = ?, role = ? WHERE id = ?;");
        $query->bind_param('ssii', $firstName, $lastName, $roleId, $id);
        return $this->make_query($query);
    }

    function update_role_using_id($id , $roleId)
    {
        $query = ($this->conn)->prepare("UPDATE users SET role = ? WHERE id = ?;");
        $query->bind_param('ii', $roleId, $id);
        return $this->make_query($query);
    }

    function change_credentials($email, $password){
        $query = ($this->conn)->prepare("UPDATE users SET email = ?, password = ? WHERE email = ?;");
        $query->bind_param('sss', $email, $password, $email);
        return $this->make_query($query);
    }

    function check_credentials($email, $password){
        $query = ($this->conn)->prepare("SELECT * FROM users WHERE email = ? && password = ?;");
        $query->bind_param('ss', $email, $password);
        return $this->make_query($query);
    }

    function check_email($email){
        $query = ($this->conn)->prepare("SELECT * FROM users WHERE email = ?;");
        $query->bind_param('s', $email);
        return $this->make_query($query);
    }

    function select_using_id($userId){
        $query = ($this->conn)->prepare("SELECT * FROM users WHERE id = ?;");
        $query->bind_param('i', $userId);
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM users;");
        return $this->make_query($query);
    }

    function select_by_id($id)
    {
        $query = ($this->conn)->prepare("SELECT * FROM users WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function select_by_email($email)
    {
        $query = ($this->conn)->prepare("SELECT * FROM users WHERE email = ?;");
        $query->bind_param('s', $email);
        return $this->make_query($query);
    }

    function upload_image($email, $imagePath){
        $query = ($this->conn)->prepare("UPDATE users SET image = ? WHERE email = ?;");
        $query->bind_param('ss', $imagePath, $email);
        return $this->make_query($query);
    }
}

/* Example Usage:
    $comment = new comments();
    $comment->delete_using_id(12);
*/

class comments extends Database{
    function __construct() {
        parent::__construct();
    }

    function insert($fromUserId, $toUserId, $comment, $depth){
        $query = ($this->conn)->prepare("INSERT INTO comments(from_user_id,to_user_id,comment,depth) VALUES(?,?,?,?);");
        $query->bind_param('iisi', $fromUserId, $toUserId, $comment, $depth);
        return $this->make_query($query);
    }

    function delete_using_id($commentId){
        $query = ($this->conn)->prepare("DELETE FROM comments WHERE id = ?;");
        $query->bind_param('i', $commentId);
        return $this->make_query($query);
    }

    function delete_using_user($userId){
        $query = ($this->conn)->prepare("DELETE FROM comments WHERE from_user_id = ? OR to_user_id = ?;");
        $query->bind_param('ii', $userId, $userId);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM comments;");
        return $this->make_query($query);
    }

    function update($commentId, $newComment){
        $query = ($this->conn)->prepare("UPDATE comments SET comment = ? WHERE id = ?;");
        $query->bind_param('si', $newComment, $commentId);
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM comments;");
        return $this->make_query($query);
    }

    function select_using_id($id){
        $query = ($this->conn)->prepare("SELECT * FROM comments WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function select_from_user($fromUserId){
        $query = ($this->conn)->prepare("SELECT * FROM comments WHERE from_user_id = ?;");
        $query->bind_param('i', $fromUserId);
        return $this->make_query($query);
    }

    function select_to_user($toUserId){
        $query = ($this->conn)->prepare("SELECT * FROM comments WHERE to_user_id = ?;");
        $query->bind_param('i', $toUserId);
        return $this->make_query($query);
    }

}

/* Example Usage:
    $roles = new roles();
    $roles->insert('admin');
*/

class roles extends Database{
    function __construct() {
        parent::__construct();
    }

    function insert($role){
        $query = ($this->conn)->prepare("INSERT INTO roles(role) VALUES(?);");
        $query->bind_param('i', $role);
        return $this->make_query($query);
    }

    function delete_using_id($roleId){
        $query = ($this->conn)->prepare("DELETE FROM roles WHERE id = ?;");
        $query->bind_param('i', $roleId);
        return $this->make_query($query);
    }

    function delete_using_name($name){
        $query = ($this->conn)->prepare("DELETE FROM roles WHERE role = ?;");
        $query->bind_param('s', $name);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM roles;");
        return $this->make_query($query);
    }

    function update($roleId, $newRole){
        $query = ($this->conn)->prepare("UPDATE roles SET role = ? WHERE id = ?;");
        $query->bind_param('si', $newRole, $roleId);
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM roles;");
        return $this->make_query($query);
    }

    function select_by_id($roleId){
        $query = ($this->conn)->prepare("SELECT * FROM roles where id = ?;");
        $query->bind_param('i', $roleId);
        return $this->make_query($query);
    }

}


/* Example Usage:
    $s = new specialties();
    $s->insert('podologista');
*/

class specialties extends Database{
    function __construct(){
        parent::__construct();
    }

    function insert($name){
        $query = ($this->conn)->prepare("INSERT INTO specialties(name) VALUES(?);");
        $query->bind_param('s', $name);
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = ($this->conn)->prepare("DELETE FROM specialties WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function delete_using_name($name){
        $query = ($this->conn)->prepare("DELETE FROM specialties WHERE name = ?;");
        $query->bind_param('s', $name);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM specialties;");
        return $this->make_query($query);
    }

    function update_specialties($specialtyId, $newName){
        $query = ($this->conn)->prepare("UPDATE specialties SET name = ? WHERE id = ?;");
        $query->bind_param('si', $newName, $specialtyId);
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM specialties;");
        return $this->make_query($query);
    }

    function select_by_id($id){
        $query = ($this->conn)->prepare("SELECT * FROM specialties WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }
}

class specialties_doctors extends Database{
    function __construct(){
        parent::__construct();
    }

    function insert($doctorsId, $specialtiesId){
        $query = ($this->conn)->prepare("INSERT INTO specialties_doctors(doctors_id, specialties_id) VALUES(?,?);");
        $query->bind_param('ii', $doctorsId, $specialtiesId);
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = ($this->conn)->prepare("DELETE FROM specialties_doctors WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }


    function delete_using_doctors_id($doctorsId){
        $query = ($this->conn)->prepare("DELETE FROM specialties_doctors WHERE doctors_id = ?;");
        $query->bind_param('i', $doctorsId);
        return $this->make_query($query);
    }

    function delete_using_specialties_id($specialtiesId){
        $query = ($this->conn)->prepare("DELETE FROM specialties_doctors WHERE specialties_id = ?;");
        $query->bind_param('i', $specialtiesId);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM specialties_doctors;");
        return $this->make_query($query);
    }

    function update_using_id($id, $specialties_id){
        $query = ($this->conn)->prepare("UPDATE specialties_doctors SET specialties_id = ? WHERE doctors_id = ?;");
        $query->bind_param('ii', $specialties_id, $id);
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM specialties_doctors;");
        return $this->make_query($query);
    }

    function select_by_specialties_id($specialtiesId){
        $query = ($this->conn)->prepare("SELECT * FROM specialties_doctors WHERE specialties_id = ?;");
        $query->bind_param('i', $specialtiesId);
        return $this->make_query($query);
    }

    function select_by_doctors_id($doctorsId){
        $query = ($this->conn)->prepare("SELECT * FROM specialties_doctors WHERE doctors_id = ?;");
        $query->bind_param('i', $doctorsId);
        return $this->make_query($query);
    }

    function check_doctor_specialty($doctorId, $specialtyId){
        $query = ($this->conn)->prepare("SELECT * FROM specialties_doctors WHERE doctors_id = ? AND specialties_id = ?;");
        $query->bind_param('ii', $doctorId, $specialtyId);
        return $this->make_query($query);
    }
}

/* Example Usage:
    $ap = new appointments();
    $ap->delete_everything();
*/

class appointments extends Database{
    function __construct(){
        parent::__construct();
    }

    function insert($doctorsId, $clientId, $confirmed, $completed, $date){
        $rand_str = generateRandomString();
        $query = ($this->conn)->prepare("INSERT INTO appointments(doctors_id,client_id,confirmed,completed,date,booked_timestamp,report_text,code) 
            VALUES(?,?,?,?,?, NOW(),NULL,?);");
        $query->bind_param('iiiiss', $doctorsId, $clientId, $confirmed, $completed, $date, $rand_str);
        return $this->make_query($query);
    }

    function set_report_text_using_id($id , $text)
    {
        $query = ($this->conn)->prepare("UPDATE  appointments SET report_text = ? WHERE id = ?;");
        $query->bind_param('si', $text, $id);
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = ($this->conn)->prepare("DELETE FROM appointments WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function delete_using_doctorClients($id){
        $query = ($this->conn)->prepare("DELETE FROM appointments WHERE doctors_id = ? OR client_id = ?;");
        $query->bind_param('ii', $id, $id);
        return $this->make_query($query);
    }

    function set_confirmed_by_id($id)
    {
        $query = ($this->conn)->prepare("UPDATE appointments SET confirmed = '1' WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function set_done_by_id($id)
    {
        $query = ($this->conn)->prepare("UPDATE appointments SET completed = '1' WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM appointments;");
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM appointments;");
        return $this->make_query($query);
    }

    function select_using_doctor_id($doctorsId){
        $query = ($this->conn)->prepare("SELECT * FROM appointments WHERE doctors_id = ?;");
        $query->bind_param('i', $doctorsId);
        return $this->make_query($query);
    }

    function select_using_client_id($clientId){
        $query = ($this->conn)->prepare("SELECT * FROM appointments WHERE client_id = ?;");
        $query->bind_param('i', $clientId);
        return $this->make_query($query);
    }

    function select_using_id($id){
        $query = ($this->conn)->prepare("SELECT * FROM appointments WHERE id = ?;");
        $query->bind_param('i', $id);
        return $this->make_query($query);
    }

    function select_using_code($code)
    {
        $query = ($this->conn)->prepare("SELECT * FROM appointments WHERE code = ?;");
        $query->bind_param('s', $code);
        return $this->make_query($query);
    }

    function select_using_date($date){
        $query = ($this->conn)->prepare("SELECT * FROM appointments WHERE date = ?;");
        $query->bind_param('s', $date);
        return $this->make_query($query);
    }

    function select_using_date_doctor_id($date, $doctorID){
        $query = ($this->conn)->prepare("SELECT * FROM appointments WHERE date = ? AND doctors_id = ?;");
        $query->bind_param('si', $date, $doctorID);
        return $this->make_query($query);
    }
}

/* Example Usage:
    $con = new contacts();
    $con->delete_everything();
*/

class contacts extends Database{
    function __construct() {
        parent::__construct();
    }

    function insert($type, $info,$date){
        $query = ($this->conn)->prepare("INSERT INTO contacts(type,information,timestamp) VALUES(?,?,?);");
        $query->bind_param('sss', $type, $info, $date);
        return $this->make_query($query);
    }

    function delete_using_id($contactId){
        $query = ($this->conn)->prepare("DELETE FROM contacts WHERE id = ?;");
        $query->bind_param('i', $contactId);
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = ($this->conn)->prepare("DELETE FROM contacts;");
        return $this->make_query($query);
    }

    function select_everything(){
        $query = ($this->conn)->prepare("SELECT * FROM contacts;");
        return $this->make_query($query);
    }

    function select_by_id($contactId){
        $query = ($this->conn)->prepare("SELECT * FROM contacts where id = ?;");
        $query->bind_param('i', $contactId);
        return $this->make_query($query);
    }

    function select_by_type($type){
        $query = ($this->conn)->prepare("SELECT * FROM contacts where type = ?;");
        $query->bind_param('s', $type);
        return $this->make_query($query);
    }

}

function validateInputs($data, $type){
    $filter = false;
    switch($type)
    {
        case 'email':
            $filter = FILTER_VALIDATE_EMAIL;    
        break;
        case 'int':
            $filter = FILTER_VALIDATE_INT;
        break;
        case 'boolean':
            $filter = FILTER_VALIDATE_BOOLEAN;
        break;
    }
    if(!$filter || filter_var($data, $filter) === false)
        return false;
    else
        return true;
    //return ($filter === false) ? false : filter_var($data, $filter) !== false ? true : false;
}

?>