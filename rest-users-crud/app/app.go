package main

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"gopkg.in/mgo.v2/bson"

	. "github.com/user/app/config"
	. "github.com/user/app/dao"
	. "github.com/user/app/models"
)

var config = Config{}
var dao = UsersDAO{}

// GET list of users
func AllUsers(w http.ResponseWriter, r *http.Request) {
	users, err := dao.FindAll()
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	retResponse(w, http.StatusOK, users)
}

// GET a flight by its ID
func FindUserId(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	user, err := dao.FindById(params["id"])
	if err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid User ID")
		return
	}
	retResponse(w, http.StatusOK, user)
}

// POST a new user
func CreateUser(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	user.ID = bson.NewObjectId()
	if err := dao.Insert(user); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	retResponse(w, http.StatusCreated, user)
}

// PUT updates an existing user
func UpdateUser(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	if err := dao.Update(user); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	retResponse(w, http.StatusOK, map[string]string{"result": "success"})
}

// DELETE an existing user
func DeleteUser(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		respondWithError(w, http.StatusBadRequest, "Invalid request payload")
		return
	}
	if err := dao.Delete(user); err != nil {
		respondWithError(w, http.StatusInternalServerError, err.Error())
		return
	}
	retResponse(w, http.StatusOK, map[string]string{"result": "success"})
}

func respondWithError(w http.ResponseWriter, code int, msg string) {
	retResponse(w, code, map[string]string{"error": msg})
}

func retResponse(w http.ResponseWriter, code int, payload interface{}) {
	response, _ := json.Marshal(payload)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	w.Write(response)
}

// Parse the configuration file 'config.toml', and establish a connection to DB
func init() {
	config.Read()
	dao.Server = config.Server
	dao.Database = config.Database
	dao.Connect()
}

// Define HTTP request routes
func main() {
	r := mux.NewRouter()
	r.HandleFunc("/users", AllUsers).Methods("GET")
	r.HandleFunc("/users", CreateUser).Methods("POST")
	r.HandleFunc("/users", UpdateUser).Methods("PUT")
	r.HandleFunc("/users", DeleteUser).Methods("DELETE")
	r.HandleFunc("/users/{id}", FindUserId).Methods("GET")
	if err := http.ListenAndServe(":3000", r); err != nil {
		log.Fatal(err)
	}
}