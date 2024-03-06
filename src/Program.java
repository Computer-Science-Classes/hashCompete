import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class Program {
    // private static final String _bookFile = "src/pride_and_prejudice.txt";
    private static final String _bookFile = "src/pride_and_prejudice.txt";
    
    public static void main(String[] args) throws IOException {
        System.out.println("Hello to the Hashing competition!");
        
        // read the book word by word and add each word to a HashWordSet
        HashWordSet hash = new HashWordSet();
        File file = new File(_bookFile);
        Scanner reader = new Scanner(file, "UTF-8");
        while(reader.hasNext()) {
            hash.add(reader.next());
        }
        reader.close();
        
        // print the hash object
        System.out.println(hash);
        
        System.out.println("Goodbye!");
    }
}
