USE `uwc_2.0`;
-- Insert MCP 
CALL InsertMCP(106.657501, 10.773045, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.653745, 10.786654, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.658821, 10.780086, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.663421, 10.775828, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.659960, 10.764715, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.662589, 10.778742, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.666257, 10.776935, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.663459, 10.782816, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.669609, 10.784208, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.664690, 10.786800, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.657961, 10.783208, RAND()*100, RAND()*100+300, 0, 0);
CALL InsertMCP(106.653347, 10.770870, RAND()*100, RAND()*100+300, 0, 0);

-- Insert vehicle
CALL InsertVehicle(106.625786, 10.810676, 0, RAND()*100+900, 'truck');
CALL InsertVehicle(106.625786, 10.810676, 0, RAND()*100+900, 'truck');
CALL InsertVehicle(106.625786, 10.810676, 0, RAND()*100+900, 'truck');
CALL InsertVehicle(106.625786, 10.810676, 0, RAND()*100+100, 'trolley');
CALL InsertVehicle(106.625786, 10.810676, 0, RAND()*100+100, 'trolley');
CALL InsertVehicle(106.625786, 10.810676, 0, RAND()*100+100, 'trolley');

-- Insert back officer
INSERT INTO `user`
VALUES (NULL,'VitNguNgok21',sha2('lulucc1122',0),'Le Van Luyen',1,0,SYSDATE(),NULL,NULL,'male',NULL,'duyvt763@gmail.com',NULL);
SET @temp_id = last_insert_id();
INSERT INTO back_officer
VALUES (@temp_id,DEFAULT,DEFAULT,DEFAULT,DEFAULT);
-- let this back officers supervise all assets
INSERT INTO asset_supervisors SELECT id, @temp_id FROM asset;

INSERT INTO `user`
VALUES (NULL,'ChienHugo33',sha2('BukBuky320',0),'Ho Thanh Than',1,0,SYSDATE(),NULL,NULL,'male',NULL,'BukBuk321@gmail.com',NULL);
SET @temp_id = last_insert_id();
INSERT INTO back_officer
VALUES (@temp_id,DEFAULT,DEFAULT,DEFAULT,DEFAULT);
INSERT INTO asset_supervisors SELECT id, @temp_id FROM asset;
SET @latest_bo_id = @temp_id;

-- Insert employee and let one back officer manages them
SET @dummy = NULL;
CALL InsertEmployee(@dummy,'trangbku123','trangthaomai212','Doan Thi Trang',@latest_bo_id,0,SYSDATE(),NULL,NULL,'female','0123567980','trangdoan@gmail.com',NULL,0,6000000);
CALL InsertEmployee(@dummy,'giaunhucho999','lotto77777','Le Van Giau',@latest_bo_id,0,SYSDATE(),NULL,NULL,'male','0987123789','ngheo12@gmail.com',NULL,1,7000000);
CALL InsertEmployee(@dummy,'Thythycute666','06052001Thy','Khuc Thy',@latest_bo_id,0,SYSDATE(),NULL,NULL,'female','0987123789','thythy99@gmail.com',NULL,0,6000000);
CALL InsertEmployee(@dummy,'VanAvt1200','123456789','Nguyen Van A',@latest_bo_id,0,SYSDATE(),NULL,NULL,'male','0977077629','Bomavt11@gmail.com',NULL,1,7000000);
CALL InsertEmployee(@dummy,'BBBboyhotrac3','BBBhotracboy44','Nguyen Van B',@latest_bo_id,0,SYSDATE(),NULL,NULL,'male','0921666111','Brherjfe1@gmail.com',NULL,0,6000000);
CALL InsertEmployee(@dummy,'123CsuiRR321','khoaito3279','Nguyen Van C',@latest_bo_id,0,SYSDATE(),NULL,NULL,'male','0125721021','Hieheit11@gmail.com',NULL,1,7000000);

-- Insert routes
INSERT INTO route
VALUES (NULL, DEFAULT, DEFAULT, NULL, @latest_bo_id);
SET @temp_id = last_insert_id();
CALL InsertMCPToRoute(1, @temp_id, 1);
CALL InsertMCPToRoute(3, @temp_id, 2);
CALL InsertMCPToRoute(4, @temp_id, 3);
CALL InsertMCPToRoute(8, @temp_id, 4);

INSERT INTO route
VALUES (NULL, DEFAULT, DEFAULT, NULL, @latest_bo_id);
SET @temp_id = last_insert_id();
CALL InsertMCPToRoute(2, @temp_id, 1);
CALL InsertMCPToRoute(6, @temp_id, 2);
CALL InsertMCPToRoute(7, @temp_id, 3);
CALL InsertMCPToRoute(9, @temp_id, 4);