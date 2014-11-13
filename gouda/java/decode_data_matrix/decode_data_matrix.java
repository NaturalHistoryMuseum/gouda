// http://javapapers.com/core-java/java-qr-code/
import java.io.FileInputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import javax.imageio.ImageIO;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.BinaryBitmap;
import com.google.zxing.ChecksumException;
import com.google.zxing.DecodeHintType;
import com.google.zxing.FormatException;
import com.google.zxing.NotFoundException;
import com.google.zxing.Result;
import com.google.zxing.client.j2se.BufferedImageLuminanceSource;
import com.google.zxing.common.HybridBinarizer;
import com.google.zxing.datamatrix.DataMatrixReader;

public class decode_data_matrix {

    public static void main(String[] args) {
        if(1==args.length) {
            System.out.println(new decode_data_matrix().decodeDataMatrix(args[0]));
        }
        else {
            System.exit(1);
        }
    }

    public static String decodeDataMatrix(String filePath) {
        Map hints = new HashMap();
        // Some options to fiddle with
        //hints.put(DecodeHintType.PURE_BARCODE, Boolean.TRUE);
        hints.put(DecodeHintType.TRY_HARDER, BarcodeFormat.DATA_MATRIX);

        try {
            BinaryBitmap binaryBitmap = new BinaryBitmap(new HybridBinarizer(
                    new BufferedImageLuminanceSource(
                            ImageIO.read(new FileInputStream(filePath)))));
            Result res = new DataMatrixReader().decode(binaryBitmap, hints);
            return res.getText();
        } catch (NotFoundException|ChecksumException|FormatException|IOException  e) {
            return "";
        }
    }
}
