package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
)

func readFile(input string, output io.Writer) error {
	var ln string
	file, err := os.Open(input)
	defer func() {
		if file != nil {
			file.Close()
		}
	}()
	if err != nil {
		return err
	}
	inputStream := bufio.NewReader(file)
	fmt.Fscanln(inputStream, &ln)
	for len(ln) > 0 && ln[0] != '#' {
		fmt.Fprintln(output, ln)
		fmt.Fscanln(inputStream, &ln)
	}
	return nil
}

func main() {
	if len(os.Args) < 3 {
		fmt.Println("At least one input file and one output file.")
		return
	}

	outputFile, err := os.Create(os.Args[len(os.Args)-1])
	if err != nil {
		fmt.Println(err)
		return
	}
	output := bufio.NewWriter(outputFile)

	for _, name := range os.Args[1 : len(os.Args)-1] {
		err = readFile(name, output)
		if err != nil {
			fmt.Printf("Error at %s: %s\n", name, err)
		}
	}

	output.Flush()
	outputFile.Close()
}
