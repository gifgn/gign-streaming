package main

import (
	"database/sql"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"net/http"
	"time"
)

func main() {
	http.HandleFunc("/time", timeHandler)
	http.HandleFunc("/auth", authHandler)
	fmt.Println("Starting on port :9876")
	http.ListenAndServe(":9876", nil)

}

func timeHandler(w http.ResponseWriter, r *http.Request) {

	t := time.Now().UTC()
	fmt.Fprintf(w, "%v", t.Unix())
}

func authHandler(w http.ResponseWriter, r *http.Request) {

	r.ParseForm()

	call := r.FormValue("call")

	if call != "publish" {
		fmt.Fprintf(w, "Cool")
		fmt.Println("Cool Play")
		return
	}

	secret := r.FormValue("secret")

	if len(secret) == 0 {
		http.Error(w, "Go away", 500) // Code 403 causes the client to try more requests
		fmt.Println("No secret")
		return
	}

	db, err := sql.Open("mysql", "gign:gignmiku@/gign")
	defer db.Close()

	err = db.Ping()
	if err != nil {
		http.Error(w, "Impossible to connect to the DB: "+err.Error(), 500)
		fmt.Println("DB Error")
		return
	}

	var username string
	err = db.QueryRow("SELECT pseudo FROM users WHERE secret=?", secret).Scan(&username)

	if err != nil {
		http.Error(w, "Go away: "+err.Error(), 500)
		fmt.Println("Bad Guy")
		return
	}

	fmt.Fprintf(w, "Cool")
	fmt.Println("Cool")
}
