package main

import (
	"fmt"
	"net/http"
	"time"
)

func main() {
	http.HandleFunc("/time", timeHandler)
	fmt.Println("Starting on port :9876")
	http.ListenAndServe(":9876", nil)

}

func timeHandler(w http.ResponseWriter, r *http.Request) {

	t := time.Now().UTC()
	fmt.Fprintf(w, "%v", t.Unix())
}
