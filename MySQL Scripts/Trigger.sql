USE `uwc_2.0`;
--
-- Constraint trigger
--
DELIMITER $$
-- Create phone number contraint
DROP TRIGGER IF EXISTS UserPhone_trigger_insert$$
CREATE TRIGGER UserPhone_trigger_insert
	BEFORE INSERT 
    ON user FOR EACH ROW
BEGIN
	DECLARE phone_mess varchar(128);
	IF (length(NEW.phone) > 10 OR (SELECT left(NEW.phone, 1)) <> '0') THEN
		SET phone_mess = concat('INSERT_Error: Phone number should have at max 10 digit, start at ‘0’: ', new.phone);
        SIGNAL sqlstate '45000' SET message_text = phone_mess;
    END IF;
END$$

DROP TRIGGER IF EXISTS UserPhone_trigger_update$$
CREATE TRIGGER UserPhone_trigger_update
	BEFORE UPDATE
    ON user FOR EACH ROW
BEGIN
	DECLARE phone_mess varchar(128);
	IF (length(NEW.phone) > 10 OR (SELECT left(NEW.phone, 1)) <> '0') THEN
		SET phone_mess = concat('INSERT_Error: Phone number should have at max 10 digit, start at ‘0’: ', new.phone);
        SIGNAL sqlstate '45000' SET message_text = phone_mess;
    END IF;
END$$

--
-- Create 18+ constraint
DROP TRIGGER IF EXISTS Birth_trigger_insert$$
CREATE TRIGGER Birth_trigger_insert
	BEFORE INSERT
    ON user FOR EACH ROW
BEGIN
	DECLARE bdate_mess varchar(128);
	IF timestampdiff(YEAR, NEW.birth, CURDATE()) < 18 THEN
		SET bdate_mess = concat('INSERT_Error: User should be over 18 years old: ', cast(new.birth as char));
		SIGNAL sqlstate '45000' SET message_text = bdate_mess;
    END IF;
END$$

DROP TRIGGER IF EXISTS Birth_trigger_update$$
CREATE TRIGGER Birth_trigger_update
	BEFORE UPDATE
    ON user FOR EACH ROW
BEGIN
	DECLARE bdate_mess varchar(128);
	IF timestampdiff(YEAR, NEW.birth, CURDATE()) < 18 THEN
		SET bdate_mess = concat('INSERT_Error: User should be over 18 years old: ', cast(new.birth as char));
		SIGNAL sqlstate '45000' SET message_text = bdate_mess;
    END IF;
END$$
--
-- Crete end time - start time contraint
DROP TRIGGER IF EXISTS end_time_trigger_insert$$
CREATE TRIGGER end_time_trigger_insert
	BEFORE INSERT
    ON worktime FOR EACH ROW
BEGIN
	DECLARE endtime_mess varchar(128);
    IF timestampdiff(SECOND, NEW.start, NEW.end) < 0 THEN
		SET endtime_mess = concat('INSERT_Error: End time should after start time: ', cast(new.start as char), ' - ', cast(new.end as char));		
		SIGNAL sqlstate '45000' SET message_text = endtime_mess;    
    END IF;
END$$

DROP TRIGGER IF EXISTS end_time_trigger_update$$
CREATE TRIGGER end_time_trigger_update
	BEFORE UPDATE
    ON worktime FOR EACH ROW
BEGIN
	DECLARE endtime_mess varchar(128);
    IF timestampdiff(SECOND, NEW.start, NEW.end) < 0 THEN
		SET endtime_mess = concat('INSERT_Error: End time should after start time: ', cast(new.start as char), ' - ', cast(new.end as char));		
		SIGNAL sqlstate '45000' SET message_text = endtime_mess;    
    END IF;
END$$
--
-- Create work radius constraint
DROP TRIGGER IF EXISTS work_radius_trigger_insert$$
CREATE TRIGGER work_radius_trigger_insert
	BEFORE INSERT
    ON janitor FOR EACH ROW
BEGIN
    IF NEW.work_radius > 500.0 THEN
		SET NEW.work_radius = 500.0;           
    END IF;
END$$

DROP TRIGGER IF EXISTS work_radius_trigger_update$$
CREATE TRIGGER work_radius_trigger_update
	BEFORE UPDATE
    ON janitor FOR EACH ROW
BEGIN
    IF NEW.work_radius > 500.0 THEN
		SET NEW.work_radius = 500.0;           
    END IF;
END$$
--
-- Create Load limt Constraint
DROP TRIGGER IF EXISTS asset_load_trigger_insert$$
CREATE TRIGGER asset_load_trigger_insert
	BEFORE INSERT
    ON asset FOR EACH ROW
BEGIN
	IF NEW.load > NEW.capacity THEN
		SET NEW.load = NEW.capacity;
	END IF;
END$$

DROP TRIGGER IF EXISTS asset_load_trigger_update$$
CREATE TRIGGER asset_load_trigger_update
	BEFORE UPDATE
    ON asset FOR EACH ROW
BEGIN
	IF NEW.load > NEW.capacity THEN
		SET NEW.load = NEW.capacity;
	END IF;
END$$
--

-- Salary > 15600 * work_time
-- => Query work_time in the month?
--
-- Employee.Status? Working or NOT Working
-- Undefind Status
--
--
-- Create Function to find the max capacity of all trucks on the same route.
DROP FUNCTION IF EXISTS GetMaxCapacity$$
CREATE FUNCTION GetMaxCapacity (route_mcp_id numeric(9, 3))
RETURNS numeric(9, 3)
DETERMINISTIC
BEGIN
	DECLARE max_cap numeric(9, 3);
    SELECT MAX(capacity) INTO max_cap
		FROM collector, employee, asset
        WHERE 
			route_mcp_id = collector.route_id AND
            asset.id = employee.vehicle_id;
	RETURN max_cap;
END$$
--
-- function to get total load of a route
DELIMITER |
DROP FUNCTION IF EXISTS `GetRouteLoad`|
CREATE FUNCTION `GetRouteLoad`(
	route_id BIGINT
)
RETURNS numeric(9,3)
DETERMINISTIC
READS SQL DATA
BEGIN
	DECLARE res NUMERIC(9,3);
	SELECT SUM(asset.`load`) INTO res
	FROM route, contains_mcp, asset
	WHERE route.id = route_id AND
		  contains_mcp.route_id = route.id AND
		  contains_mcp.mcp_id = asset.id;
	RETURN res;
END |
--
-- Create trigger to react if insert mcp overloading the truck on route.
DROP TRIGGER IF EXISTS overloaded_mcp_route_insert$$
CREATE TRIGGER overloaded_mcp_route_insert
	BEFORE INSERT
    ON contains_mcp FOR EACH ROW
BEGIN
	DECLARE mcp_overload_mess VARCHAR(128);
	IF ((GetRouteLoad(NEW.route_id) 
		+ (SELECT capacity FROM asset WHERE asset.id = NEW.mcp_id)) 
        > GetMaxCapacity(NEW.route_id)) THEN
		SET mcp_overload_mess = CONCAT('Collector Truck will be overloaded on this route if MCP: ', cast(NEW.mcp_id as char),' is added into route: ', cast(NEW.route_id as char),'.');
        SIGNAL sqlstate '45000' SET message_text = mcp_overload_mess;	
-- 		DELETE FROM contains_mcp WHERE contains_mcp.mcp_id = NEW.mcp_id AND contains_mcp.route_id = NEW.route_id;
    END IF;
END$$
--
-- DROP TRIGGER IF EXISTS overloaded_mcp_route_update$$
-- CREATE TRIGGER overloaded_mcp_route_update
-- 	BEFORE UPDATE
--     ON asset FOR EACH ROW
-- BEGIN
-- 	DECLARE mcp_overload_mess VARCHAR(128);
-- 	IF (is_vehicle = 0 AND GetRouteLoad(NEW.route_id)) 
-- 		-- + (SELECT capacity FROM asset WHERE asset.id = NEW.mcp_id)) 
--         > GetMaxCapacity(NEW.route_id) THEN
-- 		SET mcp_overload_mess = CONCAT('Collector Truck will be overloaded on this route if MCP: ', cast(NEW.mcp_id as char),' is updated on the route: ', cast(NEW.route_id as char),'.');
--         SIGNAL sqlstate '45000' SET message_text = mcp_overload_mess;	
-- -- 		DELETE FROM contains_mcp WHERE contains_mcp.mcp_id = NEW.mcp_id AND contains_mcp.route_id = NEW.route_id;
--     END IF;
-- END$$
--
-- IN Case update mcp load, need to query all route has mcp. 
-- Action? Unaccepted update/ Delete mcp from route.
--
-- Derived Attr Trigger
-- 
-- Trigger count employee of back officer
DROP TRIGGER IF EXISTS count_employee_trigger$$
CREATE TRIGGER count_employee_trigger
	AFTER INSERT 
    ON employee for each row
BEGIN
	UPDATE back_officer 
		SET employee_count = employee_count + 1
        WHERE back_officer.user_id = NEW.manager_id;
END$$
--
-- Trigger count MCP and vehicle supervised by b_o
DROP TRIGGER IF EXISTS count_mcp_trigger$$
CREATE TRIGGER count_mcp_trigger
	AFTER INSERT
    ON asset_supervisors FOR EACH ROW
BEGIN
	IF (SELECT is_vehicle FROM asset WHERE asset.id = NEW.asset_id) = 0 THEN
		-- Update MCP
		UPDATE back_officer
			SET MCP_count = MCP_count + 1
            WHERE 
				user_id = NEW.backofficer_id;
	END IF;
END$$
--
-- Trigger count vehicle supervised by b_o
DROP TRIGGER IF EXISTS count_vehicle_trigger$$
CREATE TRIGGER count_vehicle_trigger
	AFTER INSERT
    ON asset_supervisors FOR EACH ROW
BEGIN
	IF (SELECT is_vehicle FROM asset WHERE asset.id = NEW.asset_id) = 1 THEN
		-- Update Vehicle
		UPDATE back_officer
			SET vehicle_count = vehicle_count + 1
            WHERE
				user_id = NEW.backofficer_id;
	END IF;
--     SET SQL_SAFE_UPDATES = state;
END$$ 
		
--
-- Trigger count route supervised by b_o
DROP TRIGGER IF EXISTS count_route_trigger$$
CREATE TRIGGER count_route_trigger
	AFTER INSERT
    ON route FOR EACH ROW
BEGIN
	UPDATE back_officer
		SET route_count = route_count + 1
        WHERE back_officer.user_id = NEW.manager_id;
END$$
--
-- Trigger count janitors work at MCP
DROP TRIGGER IF EXISTS count_janitor_trigger$$
CREATE TRIGGER count_janitor_trigger
	AFTER INSERT
    ON janitor FOR EACH ROW
BEGIN
	UPDATE mcp
		SET janitor_count = janitor_count + 1
        WHERE mcp.asset_id = NEW.mcp_id;
END$$
--
-- Query count 
DROP FUNCTION IF EXISTS `CountMCP` $$
CREATE FUNCTION `CountMCP` (backofficer_id bigint)
RETURNS bigint
deterministic
BEGIN
	DECLARE count_mcp bigint;
    SELECT COUNT(backofficer_id) INTO count_mcp
		FROM asset_supervisors, asset
		WHERE 
			asset_supervisors.backofficer_id = backofficer_id AND
			asset_supervisors.asset_id = asset.id AND
            asset.is_vehicle = 0;
	RETURN count_mcp;
END$$
--
DROP FUNCTION IF EXISTS `CountVehicle` $$
CREATE FUNCTION `CountVehicle`(backofficer_id bigint)
RETURNS bigint
deterministic
BEGIN
	DECLARE count_vehicle bigint;
    SELECT COUNT(backofficer_id) INTO count_vehicle
		FROM asset_supervisors, asset
		WHERE 
			asset_supervisors.backofficer_id = backofficer_id AND
			asset_supervisors.asset_id = asset.id AND
            asset.is_vehicle = 1;
	RETURN count_vehicle;
END$$
--
-- Count ALL in back_officer table
DROP PROCEDURE IF EXISTS CountAll $$
CREATE PROCEDURE CountAll()
BEGIN
	DECLARE finish bool DEFAULT 0;
    DECLARE backofficer_id bigint;
    DECLARE curID CURSOR FOR SELECT user_id FROM back_officer FOR UPDATE;
    DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET finish = 1;
    OPEN curID;
    getID: LOOP
		FETCH curID INTO backofficer_id;
        IF finish = 1 THEN LEAVE getID;
        END IF;
        UPDATE back_officer
			SET MCP_count = CountMCP(backofficer_id),
				vehicle_count = CountVehicle(backofficer_id)
            WHERE user_id = backofficer_id;
    END LOOP getID;
    CLOSE curID;
END $$
--
-- Shift Insert trigger
DROP TRIGGER IF EXISTS Shift_Insert $$
CREATE TRIGGER Shift_Insert 
	BEFORE INSERT 
    ON worktime FOR EACH ROW
BEGIN
	DECLARE overload_shift_mess VARCHAR(128);
    DECLARE is_overloaded bool DEFAULT 0;
	DECLARE exit_shift bool DEFAULT 0;
    DECLARE start_time time;
	DECLARE end_time time;
	DECLARE curShift CURSOR 
		FOR SELECT `start`, `end` FROM worktime 
			WHERE 
				worktime.employee_id = NEW.employee_id AND
				worktime.weekday = NEW.weekday;
    DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET exit_shift = 1;
    OPEN curShift;
    GetShift: LOOP
		FETCH curShift INTO `start_time`, `end_time`;
        IF exit_shift = 1 THEN LEAVE GetShift;
        END IF;
        -- New start time before old end time
        IF timestampdiff(second, NEW.start, end_time) > 0 THEN
			-- New end time after old start time
            IF timestampdiff(second, NEW.end, start_time) < 0 THEN 
				SET is_overloaded = 1;
			END IF;
        END IF;
        IF (is_overloaded) THEN
			SET overload_shift_mess = CONCAT('Shift inserted must not overloading exist shifts: ', 
										cast(NEW.start as char),' - ', cast(NEW.end as char), ' on: ', cast(NEW.weekday as char));
			SIGNAL sqlstate '45000' SET message_text = overload_shift_mess;
		END IF;
    END LOOP GetShift;
    CLOSE curShift;
END $$

DELIMITER ;
