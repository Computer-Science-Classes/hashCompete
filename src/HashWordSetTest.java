import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.lang.reflect.Field;

import org.junit.Test;
import org.w3c.dom.Node;

public class HashWordSetTest {
    

    @Test
    public void testReflectionAccess() {
        HashWordSet hashSet = new HashWordSet();
        hashSet.add("testWord");

        try {
            Field elementDataField = HashWordSet.class.getDeclaredField("elementData");
            elementDataField.setAccessible(true);
            HashWordSet.Node[] elementData = (HashWordSet.Node[]) elementDataField.get(hashSet);

            assertNotNull("elementData should not be null after adding a word.", elementData);

            boolean found = false;
            for (HashWordSet.Node node : elementData) {
                if (node != null) {
                    if ("TESTWORD".equals(node.word)) {
                        found = true;
                        break;
                    }
                    while (node.next != null) {
                        node = node.next;
                        if ("TESTWORD".equals(node.word)) {
                            found = true;
                            break;
                        }
                    }
                }
                if (found) break;
            }

            assertTrue("The word 'testWord' should be found in the hash set.", found);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            fail("Reflection access failed with exception: " + e.getMessage());
        }
    }

    @Test
    public void testIterationAndCounting() {
        HashWordSet hashSet = new HashWordSet();
        hashSet.add("example");
        hashSet.add("testing");
        hashSet.add("hash");
        hashSet.add("function");

        try {
            Field elementDataField = HashWordSet.class.getDeclaredField("elementData");
            elementDataField.setAccessible(true); // Bypass the private access modifier
            HashWordSet.Node[] elementData = (HashWordSet.Node[]) elementDataField.get(hashSet); 

            int totalCount = 0;
            for (HashWordSet.Node node : elementData) {
                while (node != null) {
                    totalCount++;
                    node = node.next;
                }
            }

            int expectedCount = 4;
            assertEquals("The total count of elements should match the expected count.", expectedCount, totalCount);
        } catch (NoSuchFieldException | IllegalAccessException e) {
            fail("Failed to access or iterate over elementData due to exception: " + e.getMessage());
        }
    }
}
