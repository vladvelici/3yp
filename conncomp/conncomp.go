package main

import (
	"bufio"
	"encoding/csv"
	"flag"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
)

// Define flags.
var (
	flagRemove = flag.Int("remove", 0, "Number of edges to remove from each graph.")
	flagGraph  = flag.String("graph", "-", "Input file for an edge list csv.")
	flagOutput = flag.String("o", "processed", "Output file base name. This program actually outputs many files, depending on the number of connected components in the graph.")
)

func main() {
	flag.Parse()

	var inputStream *bufio.Reader
	if *flagGraph == "-" {
		inputStream = bufio.NewReader(os.Stdin)
	} else {
		file, err := os.Open(*flagGraph)
		if err != nil {
			fmt.Printf("Error reading input file %s\n", err.Error())
		}
		inputStream = bufio.NewReader(file)
		defer file.Close()
	}

	csvReader := csv.NewReader(inputStream)

	for {
		from, to, err := record(csvReader)
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Println("error ", err)
			return
		}
		fmt.Printf("Read pair\t %d - %d\n", from, to)
	}
}

func record(r *csv.Reader) (int, int, error) {
	rec, err := r.Read()
	if err != nil {
		return 0, 0, err
	}
	if len(rec) != 2 {
		return 0, 0, fmt.Errorf("Wrong record %#v.", rec)
	}
	rec[0], rec[1] = strings.TrimSpace(rec[0]), strings.TrimSpace(rec[1])
	a, err := strconv.Atoi(rec[0])
	if err != nil {
		return 0, 0, err
	}
	b, err := strconv.Atoi(rec[1])
	if err != nil {
		return 0, 0, err
	}
	return a, b, nil
}
