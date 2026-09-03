import java.util.*;

public class OpenCRXtoken {

  public static void main(String args[]) {
    int length = 40;
    long start = Long.parseLong(args[0]); //"1783036227142");
    long end = Long.parseLong(args[1]); //"1783036227585");

    for(long x = start; x < end; x++){
      System.out.println(getRandomBase62(length, x));
    }
  }

  public static String getRandomBase62(int length, long seed) {
    Random random = new Random(seed);
    String s = "";
    for (int i = 0; i < length; i++)
      s = s + "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".charAt(random.nextInt(62));
    return s;
  }
}
